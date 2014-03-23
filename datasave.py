# -- coding: utf-8 --
import codecs
import csv
from unidecode import unidecode
from utf8csv import unicode_csv_reader

__author__ = 'tobi'

def save_data(filename,data,delimiter=';'):
    """ saves data in a recarray to a file
    """
    with codecs.open(filename,'w+','utf-8') as fp:

        for row in data:
            line = []
            for col in data.dtype.names:
                if col in ['Date','Datum']:
                    line.append(row[col].strftime('%d/%m/%Y'))
                elif col in ['Text']:
                    line.append(row[col].replace('\n','\\\\'))
                elif col in ['Kategorie','Unterkategorie']:
                    line.append(row[col])
                elif col in ['Lastschrift']:
                    line.append('{0:.2f}'.format(row[col]))
                else:
                    line.append(str(row[col]))
            fp.write(delimiter.join(line)+'\n')

def load_data(filename):
    """ saves a recarray
    """
    pass

def load_categories(filename):
    """loads a csv file containing the categories"""

    cat = []
    with codecs.open(filename,'rb','utf-8') as fp:
        csvreader=unicode_csv_reader(fp, delimiter=';')
        for row in csvreader:
            cat.append(tuple([unidecode(r) for r in row]))
    return  cat