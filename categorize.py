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
from dialog import Dialog
from unidecode import unidecode

database = 'data/categorized.csv'
maxlines=10

if __name__=='__main__':

    d = Dialog()

    d.set_background_title('My Finances - Manual categorization')

    # ask for period of interest
    now = datetime.now()
    code, dates=d.calendar('choose start date of evaluation',year=now.year,month=now.month,day=now.day)
    start = datetime(year=dates[2],month=dates[1],day=dates[0])

    code, dates=d.calendar('choose end date of evaluation',year=now.year,month=now.month,day=now.day)
    stop = datetime(year=dates[2],month=dates[1],day=dates[0])


    # load categories
    categories = load_budget(start,stop)

    cats=zip(categories['Kategorie'].tolist(),categories['Beschreibung'].tolist())

    choices= cats+[('Delete','Delete current entry'),('Edit','Edit text of current entry')]

    # add load expenses from phone
    success=False
    d.msgbox("load data from phone.\nPlease export data in the Expenses App now...",cr_wrap=True)
    while not success:
        try:
            d.msgbox("load data from phone \nPlease connect phone to usb and switch on USB debbuging...",cr_wrap=True)
            dlist=(load_Expenses_from_phone(start,stop),)
            success = True
        except ADBException as err:
            d.msgbox("No connection to phone: ({0:d}) {1:s}".format(err.exitcode,err.strerror))

    # ask user to update his data
    d.msgbox("load data from files on this computer \nPlease download newest documents from e-finance servers...",cr_wrap=True)

    d.gauge_start("load data from PostFinance extracts... \nPlease wait one moment!",cr_wrap=True)
    callback=lambda x:d.gauge_update(int(x))
    dlist+=(load_PostFinanceData(start,stop,callback=callback),)
    d.gauge_stop()

    d.gauge_start("load data from MasterCard extracts... \nPlease wait one moment!",cr_wrap=True)
    dlist+=(load_MasterCardData(start,stop,callback=callback),)
    d.gauge_stop()

    dlist+=(load_VisaCardTransactionData(start,stop),)

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
    else:
        with codecs.open(database,'w+','utf-8') as fp:
            fp.write(';'.join(data.dtype.names)+'\n')

    with codecs.open(database,'a','utf-8') as fp:
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


            else:
                row['Hash'] = hashtag

                category = row['Kategorie']
                default_item = categories[0][0]

            text = unidecode(row['Text']).encode('utf-8')
            textlines=text.splitlines()
            if len(textlines)>maxlines:
                text = '\n'.join(textlines[:maxlines])+'...'

            table.add_row([row['Datum'].strftime('%a, %d, %B %Y').decode('utf-8').encode('utf-8'), text, 'CHF {0:.0f}'.format(row['Lastschrift']), category.encode('utf-8')])

            text = "Choose category\n\nEntry number {0:d}\n\n".format(i+1)

            print text
            print default_item

            text2 = table.draw()

            code, tag = d.menu(text+text2,height=30,width=109,menu_height=10,choices=choices,default_item=default_item)

            if code==d.CANCEL:
                break

            if tag=='Edit':
                code, row['Text'] = d.inputbox(text='Enter new text',init=unidecode(row['Text']))
                code, val_str     = d.inputbox(text='Enter new amount ',init=str(row['Lastschrift']))
                row['Lastschrift']= float(val_str)

                table = texttable.Texttable(max_width=100)
                table.set_deco(0)

                text = row['Text'].decode('utf-8').encode('utf-8')
                textlines=text.splitlines()
                if len(textlines)>maxlines:
                    text = '\n'.join(textlines[:maxlines])+'...'

                table.add_row([row['Datum'].strftime('%a, %d, %B %Y').decode('utf-8').encode('utf-8'), text, 'CHF {0:.0f}'.format(row['Lastschrift']), category.encode('utf-8')])
                code, tag = d.menu(text+table.draw(),height=30,width=108,menu_height=10,choices=choices,cr_wrap=True)

            elif tag=='Delete':
                row['Deleted']=True

            else:
                row['Kategorie']=tag

            save_data_row(fp,row,data.dtype)