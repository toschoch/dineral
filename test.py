# -- coding: utf-8 --
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule
import datetime
from unidecode import unidecode
from datacollect import load_Expenses_from_phone
from dataload import *
from dataplot import calculate_statistics, plot_category
from datasave import load_data
from utils import firstOf, lastOf
import matplotlib.pyplot as plt

__author__ = 'tobi'



if __name__ == '__main__':

    data = load_PostFinancePaymentConfirmation(r"/home/tobi/Finance/Konto Dokumente/Kontos Post/Zahlungsbestätigungen/2013-06-28.pdf")

    print data


