# -- coding: utf-8 --
from datasave import save_data, load_categories

__author__ = 'tobi'

import re
from dataload import *
from datacollect import *
from matplotlib.mlab import rec_join, rec_append_fields
import numpy as np
import numpy.lib.recfunctions as recfun
import hashlib
import texttable
from dialog import Dialog
from unidecode import unidecode

categories = load_categories('categories.txt')
database = 'categorized.csv'

choices= categories+[('Delete','Delete current entry'),('Edit','Edit text of current entry')]

if __name__=='__main__':

    d = Dialog()

    d.set_background_title('My Finances - Manual categorization')

    # ask for period of interest
    now = datetime.now()
    code, dates=d.calendar('choose start date of evaluation',year=now.year,month=now.month,day=now.day)
    start = datetime(year=dates[2],month=dates[1],day=dates[0])

    code, dates=d.calendar('choose end date of evaluation',year=now.year,month=now.month,day=now.day)
    stop = datetime(year=dates[2],month=dates[1],day=dates[0])


    # add load expenses from phone
    success=False
    d.msgbox("load data from phone.\nPlease export data in the Expenses App now...")
    while not success:
        try:
            d.msgbox("load data from phone \nPlease connect phone to usb and switch on USB debbuging...")
            dlist=(load_Expenses_from_phone(start,stop),)
            success = True
        except ADBException:
            pass

    d.gauge_start("load data from PostFinance extracts... Please wait one moment!")
    callback=lambda x:d.gauge_update(int(x))
    dlist+=(load_PostFinanceData(start,stop,callback=callback),)
    d.gauge_stop()

    d.gauge_start("load data from MasterCard extracts... Please wait one moment!t")
    dlist+=(load_MasterCardData(start,stop,callback=callback),)
    d.gauge_stop()

    dlist+=(load_VisaCardTransaction(r'transactions.csv'),)

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

    with open('categorized.csv','w+') as fp:
        fp.write(';'.join(data.dtype.names)+'\n')

    for i,row in enumerate(data):

        row['Hash'] = hashlib.md5(row['Datum'].strftime('%d-%m-%Y')+' '+unidecode(row['Text'])+' '+'CHF {0:.0f}'.format(row['Lastschrift'])).hexdigest()

        table = texttable.Texttable(max_width=100)
        table.set_deco(0)
        table.add_row([row['Datum'].strftime('%a, %d, %B %Y'), unidecode(row['Text']), 'CHF {0:.0f}'.format(row['Lastschrift']), row['Kategorie']])

        text="Choose category\n\n\nEntry number {0:d}\n\n".format(i+1)

        code, tag = d.menu(text+table.draw(),height=30,width=108,menu_height=10,choices=choices)

        if code==d.CANCEL:
            break



        if tag=='E':
            code, row['Text'] = d.inputbox(text='Enter new text',init=unidecode(row['Text']))

            table = texttable.Texttable(max_width=100)
            table.set_deco(0)
            table.add_row([row['Datum'].strftime('%a, %d, %B %Y'), unidecode(row['Text']), 'CHF {0:.0f}'.format(row['Lastschrift']), row['Kategorie']])
            code, tag = d.menu(text+table.draw(),height=30,width=108,menu_height=10,choices=choices)

        elif tag=='D':
            row['Deleted']=True

        else:
            row['Kategorie']=tag

        save_data(database,data)