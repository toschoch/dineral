# -- coding: utf-8 --
import codecs
from datetime import datetime
import numpy as np
from unidecode import unidecode
from utf8csv import unicode_csv_reader
from matplotlib.mlab import rec_drop_fields

__author__ = 'tobi'

def save_data(filename,data,delimiter=';'):
    """ saves data in a recarray to a file
    """
    with codecs.open(filename,'w+','utf-8') as fp:

        # write header
        fp.write(delimiter.join(data[0].dtype.names)+'\n')

        for row in data:
            save_data_row(fp,row,data[0].dtype,delimiter)


def save_data_row(fp,row,dtype,delimiter=';'):
    """ write one new line in file pointer
    """
    line = []
    for col in dtype.names:
        if col in ['Date','Datum']:
            line.append(row[col].strftime('%d/%m/%Y'))
        elif col in ['Text']:
            line.append(row[col].replace('\n','\\\\'))
        elif col in ['Kategorie','Unterkategorie']:
            line.append(unicode(row[col]))
        elif col in ['Lastschrift']:
            line.append('{0:.2f}'.format(row[col]))
        else:
            line.append(unicode(row[col]))
    fp.write(delimiter.join(line)+'\n')

    return

def load_data(filename,delimiter=';'):
    """ loads a recarray
    """
    with codecs.open(filename,'r','utf-8') as fp:

        data=[]
        i=0
        csvreader = unicode_csv_reader(fp,delimiter=delimiter)
        for row in csvreader:

            if i==0:
                header=row
            else:
                line=[]
                for col,d in zip(header,row):
                    if col in ['Date','Datum']:
                        line.append(datetime.strptime(d,'%d/%m/%Y'))
                    elif col in ['Text']:
                        line.append(d.replace('\\\\','\n'))
                    elif col in ['Kategorie','Unterkategorie']:
                        line.append(d)
                    elif col in ['Lastschrift','Summe','Total','Jahresbudget']:
                        line.append(float(d))
                    elif col in ['Deleted']:
                        if d == 'True':
                            line.append(True)
                        else:
                            line.append(False)
                    else:
                        line.append(unicode(d))
                data.append(line)
            i+=1

    return np.rec.fromrecords(data,names=header)