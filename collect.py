# -- coding: utf-8 --
__author__ = 'tobi'

import re
from dataload import *
from datacollect import *
from matplotlib.mlab import rec_join, rec_append_fields
import numpy as np
import numpy.lib.recfunctions as recfun
import os
import glob
import sys
import subprocess
import texttable
from dialog import Dialog
from  unidecode import  unidecode

cat = ['Miete','Mobiliar',u'Einkauf/Essen','Transport','Eishockey','Sport allgemein','Mobilabo','Spenden','Ausbildung','Versicherungen','Krankenkasse','Medizin','Steuern',
       'Bussen','Bekleidung','Anschaffungen','Ausgang',u'Reisen/Ausflüge',u'Bücher','Geschenke']

choices= [('('+str(i)+')',c)for i,c in enumerate(cat)]

if __name__=='__main__':

    d = Dialog()

    d.set_background_title('My Finances')

    now = datetime.now()
    code, dates=d.calendar('choose start date for evaluation',year=now.year,month=now.month,day=now.day)
    datum = datetime(year=dates[2],month=dates[1],day=dates[0])


    d.infobox("load all data newer than "+datum.strftime('%a, %d, %B %Y')+"... \nPlease wait one moment")
    #     i_chosen=int(input1)
    #box('load data from different sources. One moment please...')
    # add load from expenses
    list0=load_Expenses('export.csv')
    list1=load_PostFinanceData(datum)
    # list2=load_MasterCardExtract(r'Januar.pdf')
    list3=load_VisaCardTransaction(r'transactions.csv')

    # join table
    joined = recfun.stack_arrays((list0,list1,list3), autoconvert=True)
    joined = expand_EFinance(joined)


    joined.sort(order='Datum')

    for i,row in enumerate(joined):

        table = texttable.Texttable(max_width=100)
        table.set_deco(0)
        table.add_row([row['Datum'].strftime('%a, %d, %B %Y'), unidecode(row['Text']), 'CHF {0:.0f}'.format(row['Lastschrift'])])

        text="Choose category\n\n\nEntry number {0:d}\n\n".format(i+1)

        code, tag = d.menu(text+table.draw(),height=30,width=108,menu_height=10,choices=choices)

        if code==d.CANCEL:
            break

        row['Kategorie']=cat[int(tag.strip('(').strip(')'))]
    #
    #     # E-Finance transaction open corresponding zahlungsbestaetigung
    #
    #     # funktion Text aendern
    #     # funktion split entry in zwei entries
    #     # funktion remove entry
    #
    #
    print joined