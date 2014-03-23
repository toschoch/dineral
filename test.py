# -- coding: utf-8 --
from dateutil.relativedelta import relativedelta
from datacollect import load_Expenses_from_phone
from dataload import *

__author__ = 'tobi'


if __name__ == '__main__':

    print load_MasterCardExtract(ur'/home/tobi/Finance/e-Rechnungen/Mastercard/2014/Februarx    .pdf')
