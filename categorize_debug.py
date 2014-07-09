# -- coding: utf-8 --
__author__ = 'tobi'

import re
from dataload import *
from datacollect import *
from matplotlib.mlab import rec_append_fields
from datasave import save_data, save_data_row, load_data
import numpy as np
import numpy.lib.recfunctions as recfun
import hashlib
import texttable
from unidecode import unidecode

database = 'data/categorized.csv'
maxlines=10

if __name__=='__main__':


    # ask for period of interest
    now = datetime.now()
    start = datetime(year=2014,month=01,day=01)

    stop = datetime(year=2014,month=05,day=31)


    # load categories
    categories = load_budget(start,stop)

    cats=zip(categories['Kategorie'].tolist(),categories['Beschreibung'].tolist())

    # dlist=(load_PostFinanceData(start,stop),)

    dlist=(load_MasterCardData(start,stop),)

    # dlist+=(load_VisaCardTransactionData(start,stop),)

    # join table
    data = recfun.stack_arrays(dlist, autoconvert=True)
    data = expand_EFinance(data)

    # assure data is in period
    data = data[np.logical_and(data['Datum']>=start,data['Datum']<=stop)]

    # add delete
    data = rec_append_fields(data,'Deleted',[False]*len(data))

    # add hashkey
    data = rec_append_fields(data,'Hash',['']*len(data),dtypes=['S32'])

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


    for i,row in enumerate(data):

        table = texttable.Texttable(max_width=100)
        table.set_deco(0)

        hashtag = hashlib.md5(unidecode(row['Datum'].strftime('%d-%m-%Y').decode('utf-8'))+' '+unidecode(row['Text'])+' '+'CHF {0:.0f}'.format(row['Lastschrift'])).hexdigest()
        if dblookup:
            I=np.nonzero(db.Hash==hashtag)[0]
            if len(I)>0:
                category = db['Kategorie'][I][0]
                default_item = category
                if category == "Keine" and db['Deleted'][I][0]:
                    default_item = "Delete"
                    category = "DELETED"
                row = dbnew[I[0]]
            else:
                category = row['Kategorie']
                default_item = categories[0][0]
                row['Hash'] = hashtag
                dbnew.append(row)
        else:
            category = row['Kategorie']
            default_item = categories[0][0]
            row['Hash'] = hashtag

        text = unidecode(row['Text']).encode('utf-8')
        textlines=text.splitlines()
        if len(textlines)>maxlines:
            text = '\n'.join(textlines[:maxlines])+'...'

        table.add_row([row['Datum'].strftime('%a, %d, %B %Y').decode('utf-8').encode('utf-8'), text, 'CHF {0:.0f}'.format(row['Lastschrift']), category.encode('utf-8')])

        text = "Choose category\n\nEntry number {0:d}\n\n".format(i+1)

        print text
        print default_item

        text2 = table.draw()


        if not dblookup:
            with codecs.open(database,'a','utf-8') as fp:
                save_data_row(fp,row,data.dtype)
        else:
            save_data(database,dbnew)
