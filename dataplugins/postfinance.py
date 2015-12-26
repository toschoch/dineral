#!/usr/bin/env python
# encoding: utf-8
"""
postfinance.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)

from abstract import DataPlugin
import subprocess
import codecs,os,datetime,glob
import pandas as pd


class PostFinance(DataPlugin):
    """ Load data account extracts from PostFinance """

    TYPE = DataPlugin.DIR

    Extracts_Path = "Konto Auszüge Postkonto"
    Confirmation_Path = "Zahlungsbestätigungen"

    def representation(self):
        return "{}/{{{}, {}}}/".format(self.properties,self.Extracts_Path,self.Confirmation_Path)

    def load_data(self, period_from, period_to, callback=None):

        start = datetime.date(period_from.year,period_from.month,1)

        new = []
        extracts_path = os.path.join(self.properties,self.Extracts_Path)
        matches=glob.glob(os.path.join(extracts_path, '*.pdf'))

        files2load=[]
        for fname in matches:

            _, name = os.path.split(fname)
            name, _ = os.path.splitext(name)

            month=datetime.datetime.strptime(name, '%Y-%m').date()
            if month>= start and month<=period_to:
                files2load.append(fname)

        prog=0
        if len(files2load)>0:
            dprog=100./len(files2load)
        else:
            dprog=0

        if len(files2load)<1:
            log.info("No files found for selected period!")
        else:
            log.info("load files: {}".format(", ".join(files2load)))

        for fname in files2load:
            newrows = self.load_PostFinanceExtract(fname)
            new.append(newrows)
            prog+=dprog
            if callback is not None:
                callback(prog)

        if len(new)>0:
            data = pd.concat(new,axis=0)
            log.info("loaded {} entries for PostFinance extracts".format(len(data)))
            data = self.expand_EFinance(data)
        else:
            data = pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)

        return data

    def load_PostFinanceExtract(self, filename):
        """ loads data from a pdf file and parses the information respect to the format description

            Parameters
            ----------
            filename:           (str) path to file to be loaded

            Returns
            -------
            (pandas DataFrame) table with data columns: date, description, amount

        """
        subprocess.call(['pdftotext','-layout',filename])

        filename = filename.replace('.pdf','.txt')

        column_headers=['Datum','Text','Gutschrift','Lastschrift','Valuta','Saldo']
        align=[0,0,1,1,1,2]

        with codecs.open(filename,'rb','utf-8') as fp:

            lines = fp.read().splitlines()

        os.remove(filename)

        table=[]

        it = iter(lines)

        try:
            while True:

                line = it.next()

                # search for column headers
                col_index = [line.find(col) for col in column_headers]

                # if column headers found -> store indices
                if min(col_index)>=0:

                    line = it.next()

                    # while no new page started, first character not space
                    while (len(line)==0 or line[0]==' '):

                        line = it.next()
                        if line.strip().startswith('Bitte') or line=='':
                            break

                        # while no new entry started
                        dataentry=[[] for col in column_headers]
                        while line<>'' and line[0]==' ':

                            # parse columns
                            for i,col in enumerate(column_headers):

                                I = col_index[i]
                                if i+1 < len(column_headers):
                                    if align[i]==0:
                                        J = col_index[i+1]
                                    elif align[i]>0:
                                        J = I+len(col)
                                else:
                                    J = I+len(col)

                                data = line.__getitem__(slice(I,J)).strip()
                                if data <> '': dataentry[i].append(data)

                            line = it.next()

                        row = ['\n'.join(col) for col in dataentry]

                        # copy date to each line
                        if row[0]=='':
                            for date in reversed(table):
                                if date[0]<>'':
                                    break
                            row[0]=date[0]

                        # append to table
                        table.append(row)

        except StopIteration:
            pass

        # crop and convert types
        rec=pd.DataFrame(table,columns=column_headers)
        out_columns=['Datum','Text','Lastschrift']
        date = [datetime.datetime.strptime(d_str,'%d.%m.%y') for d_str in rec.Datum]
        import numpy as np
        amount  = np.array([float(f_str.replace(' ','')) if f_str<>'' else 0. for f_str in rec.Lastschrift ])
        amount += np.array([-float(f_str.replace(' ','')) if f_str<>'' else 0. for f_str in rec.Gutschrift ])
        text = [t_str for t_str in rec.Text]
        I = amount <> 0.
        rec = pd.DataFrame(dict(zip(out_columns,[date,text,amount])))[I]

        I = (rec.Text<>'Total')

        rec = pd.DataFrame(rec[I],columns=out_columns)
        rec.Datum = pd.DatetimeIndex(rec.Datum).date

        rec['Kategorie']=self.NOCATEGORY

        return rec

    def expand_EFinance(self, data):
        """ expand all unspecific E-Finance entries with the corresponding entries from the payment confirmation

            Parameters
            ----------
            data:           (numpy.rec.recarray) table with data

            Returns
            -------
            (numpy.rec.recarray) table with data, columns: date, description, amount

        """
        import  numpy as np
        I = data['Text'].str.startswith('E-FINANCE AUFTRAG')
        log.info("found {} E-Finance transactions, try to expand...".format(I.sum()))

        new = []
        for i,row in data[I].iterrows():

            try:
                confirmation_path = os.path.join(self.properties,self.Confirmation_Path)
                pdffile = glob.glob(os.path.join(confirmation_path, row['Datum'].strftime('%Y-%m-%d') + u'.pdf'))[0]
                newrows = self.load_PostFinancePaymentConfirmation(pdffile)
                new.append(newrows)
            except IndexError:
                pass

        new.append(data[np.logical_not(I)])

        if len(new)>0:
            new = pd.concat(new, axis=0)
        else:
            new = pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)

        return new

    def load_PostFinancePaymentConfirmation(self, filename):
        """ loads data from a pdf file and parses the information respect to the format description

            Parameters
            ----------
            filename:           (str) path to file to be loaded

            Returns
            -------
            (numpy.rec.recarray) table with data, columns: date, description, amount

        """
        subprocess.call(['pdftotext','-layout',filename])

        filename = filename.replace('.pdf','.txt')

        column_headers=['Whg','Transaktionsart','Betrag','Währung','Betrag','Kurs','Betrag in CHF']

        align=[0,0,1,1,1,2]

        with codecs.open(filename,'rb','utf-8') as fp:

            lines = fp.read().splitlines()

        os.remove(filename)

        table=[]

        it = iter(lines)

        try:
            while True:

                line = it.next()

                if line.lstrip().startswith('Total'):
                    break

                if line.find(u'Ausführungsdatum:')>=0:
                    data=line.split(':')[-1].strip()
                    data=datetime.datetime.strptime(data,"%d.%m.%Y")

                # search for column headers
                col_index = [line.find(col) for col in column_headers]


                # if column headers found -> store indices
                if min(col_index)>=0:

                    line = it.next()
                    line = it.next()
                    line = it.next()

                    # while no new page started, first character not space
                    while not line.lstrip().startswith('Total'):

                        if line=='':
                            line=it.next()
                            continue

                        # while no new entry started
                        dataentry=[None,[],None]
                        dataentry[2]=float(line[col_index[6]:].replace(' ',''))
                        dataentry[0]=data
                        firstline = False
                        line = it.next()
                        while not line.lstrip().startswith('CHF') and len(line)>0:

                            # parse columns
                            dataentry[1].append(line.strip().replace('   ',''))

                            line = it.next()

                        dataentry[1]='\n'.join(dataentry[1])

                        # append to table
                        table.append(dataentry)

        except StopIteration:
            pass

        rec = pd.DataFrame(table,columns=['Datum','Text','Lastschrift'])

        rec.Datum = pd.DatetimeIndex(rec.Datum).date

        rec['Kategorie']=self.NOCATEGORY

        return rec