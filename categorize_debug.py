# -- coding: utf-8 --
import pickle

__author__ = 'tobi'

import re
from dataload import *
from datacollect import *
from matplotlib.mlab import rec_append_fields,rec2txt
from datasave import save_data, save_data_row, load_data
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


    # ask for period of interest
    start = datetime(year=2015,month=5,day=1)

    stop = datetime(year=2015,month=5,day=11)

    print load_Expenses_from_Dropbox(start,stop)