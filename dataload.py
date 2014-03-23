# -- coding: utf-8 --
from utf8csv import unicode_csv_reader
import numpy as np
from datetime import datetime
import csv
import os
import subprocess
from io import StringIO
import codecs
from matplotlib.mlab import rec_append_fields,rec_drop_fields

__author__ = 'tobi'

def load_Expenses(filename):
    """ load data from a expenses csv file

        Parameters
        ----------
        filename:           (str) path to file to be loaded

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    convert={
        'Date':lambda x: datetime.strptime(x,'%d.%m.%Y'),
        'Amount': lambda x: -float(x.rstrip(' CHF').replace('.','').replace(',','.')),
        'Note': lambda x: x.strip("'")}

    # read data
    with codecs.open(filename, 'r','utf-8') as f:
        lines=f.read().splitlines()

    header=lines.pop(0).split(';')
    data=[]
    for line in lines:

        dline=[]
        for c,h in zip(line.split(';'),header):
            try:
                dline.append(convert[h](c))
            except KeyError:
                dline.append(c)
        data.append(dline)

    rec = np.rec.fromrecords(data,names=['Datum','Kategorie','Unterkategorie','Lastschrift','Text'])
    return rec



def load_VisaCardTransaction(filename):
    """ load data from a transaction csv file

        Parameters
        ----------
        filename:           (str) path to file to be loaded

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """
    data=[]
    with codecs.open(filename, 'rb',"utf-16") as f:
        reader = unicode_csv_reader(f,quotechar='"',delimiter='\t')
        for i,row in enumerate(reader):
            if i==0:
                header=row
            else:
                data.append(row)


    data=np.rec.fromrecords(data,names=header)
    conv1 = lambda x: datetime.strptime(x,'%d.%m.%Y')
    conv2 = lambda x: float(x)
    conv3 = lambda x: x.replace('\r\n','\n')
    cdata=[]
    for i,c in enumerate(header):
        if i==0:
            cdata.append(map(conv1,data[c]))
        elif i==len(header)-2:
            cdata.append(map(conv2,data[c]))
        else:
            cdata.append(map(conv3,data[c]))

    rec = np.rec.fromarrays(cdata,names=('Datum', 'Text', 'Sektor', 'Rechnung', 'Lastschrift', 'Gutschrift'))
    rec = rec_drop_fields(rec,['Sektor','Rechnung','Gutschrift'])

    rec=rec_append_fields(rec,['Kategorie','Unterkategorie'],[['Keine']*len(rec),['Keine']*len(rec)])

    return rec

def load_MasterCardExtract(filename):
    """ loads data from a pdf file and parses the information respect to the format description

        Parameters
        ----------
        filename:           (str) path to file to be loaded

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """
    # parse pdf to text
    os.system('./SecuredPDF2txt.sh '+filename)
    filename=filename.replace('.pdf','.txt')

    column_headers=['Datum','Text','Belastungen','Gutschriften','Datum']
    align=[0,0,1,1,1,2]

    with codecs.open(filename,'r','utf-8') as fp:
        lines = fp.read().splitlines()

    # remove the text file
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
                line = it.next()


                # while no new page started, first character not space
                while line.find('UEBERTRAG AUF DIE NAECHSTE SEITE')<0 or line.find('Saldo zu unseren Gunsten')<0:

                    # try to parse date
                    try:
                        date=line.split(' ')[0]
                        date=datetime.strptime(date,"%d.%m.%y")

                    except (IndexError,ValueError):
                        line = it.next()
                        continue

                    # except saldovortrag and ESR-ZAHLUNG
                    if line.find('SALDOVORTRAG')>=0 or line.find('IHRE ESR-ZAHLUNG')>=0:
                        line = it.next()
                        continue

                    text=[' '.join(line.split(' ')[1:-2])]
                    f_str = line.split(' ')[-2]
                    amount=float(f_str)

                    # try to parse date
                    while True:
                        line = it.next()
                        try:
                            d=line.split(' ')[0]
                            d=datetime.strptime(d,"%d.%m.%y")

                            table.append([date,'\n'.join(text),amount])

                            break

                        except (IndexError,ValueError):
                            if line=='':continue
                            if line.find('UEBERTRAG AUF NAECHSTE SEITE')>=0 or line.find('Saldo zu unseren Gunsten')>=0:
                                table.append([date,'\n'.join(text),amount])
                                break
                            text.append(line)

    except StopIteration:
        pass

    # crop and convert types
    headers=['Datum','Text','Lastschrift']
    rec=np.rec.fromrecords(table,names=headers)

    rec=rec_append_fields(rec,['Kategorie','Unterkategorie'],[['Keine']*len(rec),['Keine']*len(rec)])

    return rec

def load_PostFinanceExtract(filename):
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
    rec=np.rec.fromrecords(table,names=column_headers)
    out_columns=['Datum','Text','Lastschrift']
    date = [datetime.strptime(d_str,'%d.%m.%y') for d_str in rec.Datum]
    amount = np.array([float(f_str.replace(' ','')) if f_str<>'' else 0. for f_str in rec.Lastschrift ])
    text = [t_str for t_str in rec.Text]
    I = amount <> 0.
    rec = np.rec.fromarrays([date,text,amount],names=out_columns)[I]

    # remove total, Bargeldbezug, Kreditkarten
    I = (rec.Text<>'Total')
    I = np.logical_and(I,rec.Text.find('BARGELD')<0)
    I = np.logical_and(I,rec.Text.find('Bargeld')<0)
    I = np.logical_and(I,rec.Text.find('KREDIT')<0)

    rec = np.rec.fromrecords(rec[I],dtype=rec.dtype)

    rec=rec_append_fields(rec,['Kategorie','Unterkategorie'],[['Keine']*len(rec),['Keine']*len(rec)])

    return rec

def load_PostFinancePaymentConfirmation(filename):
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

    column_headers=[u'Whg',u'Transaktionsart',u'Betrag',u'Währung',u'Betrag',u'Kurs',u'Betrag in CHF']

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
                data=datetime.strptime(data,"%d.%m.%Y")

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
                    dataentry[2]=float(line.split()[-1])
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

    rec = np.rec.fromrecords(table,names=['Datum','Text','Lastschrift'])

    rec=rec_append_fields(rec,['Kategorie','Unterkategorie'],[['Keine']*len(rec),['Keine']*len(rec)])

    return rec