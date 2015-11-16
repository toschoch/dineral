# -- coding: utf-8 --
import pickle

__author__ = 'tobi'

import re
from dataload import *
import datetime
from datacollect import *
from matplotlib.mlab import rec_append_fields
from datasave import save_data, load_data
import numpy as np
import numpy.lib.recfunctions as recfun
import hashlib
import texttable
from dialog import Dialog
from unidecode import unidecode

database = 'data/categorized.csv'
clf_file = 'data/classifier.pickle'
maxlines=10

if __name__=='__main__':

    start = datetime(2015,1,1)
    stop = datetime(2015,8,1)

    # budget = load_budget(start,stop)

    data = pd.read_csv('temp.csv',delimiter=';',parse_dates=['Datum'])

    print data.Datum