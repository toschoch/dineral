import re

__author__ = 'tobi'

from dataload import load_PostFinanceExtract,load_MasterCardExtract,load_VisaCardTransaction
from matplotlib.mlab import rec_join, rec_append_fields
import numpy as np
import numpy.lib.recfunctions as recfun
import os

cat = ['Miete','Mobiliar',u'Einkauf/Essen','Transport','Eishockey','Sport allgemein','Mobilabo','Spenden','Ausbildung','Versicherungen','Krankenkasse','Medizin','Steuern',
       'Bussen','Bekleidung','Anschaffungen','Ausgang',u'Reisen/Ausfluege',u'Bue2cher','Geschenke']

if __name__=='__main__':

    # add load from expenses

    list1=load_PostFinanceExtract(r'2014-01.pdf')
    list2=load_MasterCardExtract(r'Januar.pdf')
    list3=load_VisaCardTransaction(r'transactions.csv')

    # join table
    joined = recfun.stack_arrays((list1,list2,list3), autoconvert=True)

    joined.sort(order='Datum')

    for i,row in enumerate(joined):

        os.system('clear')

        print 'Entry: ' + repr(row) + '\n'

        print 'choose category'

        print '  '.join([str(j)+') '+c for j,c in enumerate(cat)])

        input1 = raw_input()
        while not re.match("^-?[0-9]+$", input1):
            print "The only valid inputs are numbers"
            input1 = raw_input()

        i_chosen=int(input1)

        row['Kategorie']=cat[i_chosen]

        # E-Finance transaction open corresponding zahlungsbestaetigung

        # funktion Text aendern
        # funktion split entry in zwei entries
        # funktion remove entry


    print joined