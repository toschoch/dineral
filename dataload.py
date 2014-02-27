__author__ = 'tobi'

import numpy as np
from datetime import datetime

def load_VisaCardTransaction(filename):
    """ load data from a transaction csv file

        Parameters
        ----------
        filename:           (str) path to file to be loaded

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """
    headers=["Date","Transaction","Sector/Partner","Invoiced","Debit","Credit"]

    data=np.loadtxt(filename,
                    dtype={'names': headers, 'formats': ('S200', 'S200','S200', 'S200', 'f8','S2')},
                    skiprows=1)

    return data

def load_MasterCardExtract(filename):
    """ loads data from a pdf file and parses the information respect to the format description

        Parameters
        ----------
        filename:           (str) path to file to be loaded

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    column_headers=['Datum','Text','Belastungen','Gutschriften','Datum']
    align=[0,0,1,1,1,2]

    with open(filename,'r') as fp:

        lines = fp.read().splitlines()

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
                            if line.find('UEBERTRAG AUF DIE NAECHSTE SEITE')>=0 or line.find('Saldo zu unseren Gunsten')>=0:
                                table.append([date,'\n'.join(text),amount])
                                break
                            text.append(line)

    except StopIteration:
        pass

    # crop and convert types
    headers=['Datum','Text','Lastschrift']
    rec=np.rec.fromrecords(table,names=column_headers)

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

    column_headers=['Datum','Text','Gutschrift','Lastschrift','Valuta','Saldo']
    align=[0,0,1,1,1,2]

    with open(filename,'r') as fp:

        lines = fp.read().splitlines()

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

    # remove total
    I = (rec.Text<>'Total')

    rec = np.rec.fromrecords(rec[I],dtype=rec.dtype)

    return rec