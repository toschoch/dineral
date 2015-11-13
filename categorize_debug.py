from __future__ import unicode_literals
# -- coding: utf-8 --
import pickle

__author__ = 'tobi'

import re
from dataload import *
import datetime
from datacollect import *
from matplotlib.mlab import rec_append_fields
from datasave import save_data, save_data_row, load_data
import numpy as np
import numpy.lib.recfunctions as recfun
import hashlib
import texttable
from dialog import Dialog
from unidecode import unidecode

database = 'data/categorized.csv'
clf_file = 'data/classifier.pickle'
maxlines=10

if __name__=='__main__':


    # ask for period of interest
    start = datetime(year=2015,month=10,day=1)

    stop = datetime(year=2015,month=10,day=31)

    # load categories
    categories = load_budget(start,stop)

    cats=zip(categories['Kategorie'].tolist(),categories['Beschreibung'].tolist())

    choices= cats+[('Delete','Delete current entry'),('Edit','Edit text of current entry')]

    dlist = []
    dlist.append(load_Expenses_from_Dropbox(start,stop))
    dlist.append(load_PostFinanceData(start,stop))
    dlist.append(load_MasterCardData(start,stop))

    # join table
    data = recfun.stack_arrays(dlist, autoconvert=True)
    data = expand_EFinance(data)

    # assure data is in period
    data = data[np.logical_and(data['Datum']>=start,data['Datum']<=stop)]

    # add delete
    data = rec_append_fields(data,str('Deleted'),[False]*len(data))

    # add hashkey
    data = rec_append_fields(data,str('Hash'),['']*len(data),dtypes=['S32'])

    # sort table
    I = np.argsort(data['Datum'])
    data = data[I]

    dblookup = False
    if os.path.isfile(database):
        dblookup = True
        db=load_data(database)
        dbnew=[row for row in db]
    else:
        with codecs.open(database,'w+','utf-8') as fp:
            fp.write(';'.join(data.dtype.names)+'\n')

    clf_available = False
    if os.path.isfile(clf_file):
        clf_available = True
        with open(clf_file,'rb') as fp:
            clf = pickle.load(fp)


    for i,row in enumerate(data):

        table = texttable.Texttable(max_width=100)
        table.set_deco(0)

        hashtag = hashlib.md5(unidecode(row['Datum'].strftime('%d-%m-%Y').decode('utf-8'))+' '+unidecode(row['Text'])+' '+'CHF {0:.0f}'.format(row['Lastschrift'])).hexdigest()
        if dblookup:
            I=np.nonzero(db.Hash==hashtag)[0]
            if len(I)>0:
                category = db['Kategorie'][I][0]
                default_item = category
                if db['Deleted'][I][0]:
                    default_item = "Delete"
                    category = "Delete"
                row = dbnew[I[0]]

            else: # no entry in db
                category = row['Kategorie']
                # use classifier to get a guess
                if clf_available:
                    default_item = clf.classes_names[clf.predict([row['Text']])[0]]
                else:
                    default_item = categories[0][0]
                row['Hash'] = hashtag
                dbnew.append(row)

        else: # no db
            category = row['Kategorie']
            default_item = categories[0][0]
            row['Hash'] = hashtag

        if category == "":
            category = " "
            default_item = categories[0][0]

        text = row['Text'].encode('utf-8')
        textlines=text.splitlines()
        if len(textlines)>maxlines:
            text = '\n'.join(textlines[:maxlines])+'...'

        table.add_row([row['Datum'].strftime('%a, %d, %B %Y').decode('utf-8').encode('utf-8'), text, 'CHF {0:.0f}'.format(row['Lastschrift']), category.encode('utf-8')])

        text = "Choose category\n\nEntry number {0:d}\n\n".format(i+1)

        text2 = table.draw()

        alltext = text+text2
        alltext = alltext.decode('utf-8')
        alltext = alltext.encode('utf-8')

        print alltext
