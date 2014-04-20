# -- coding: utf-8 --
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import texttable
from unidecode import unidecode
from datacollect import load_budget
from dataplot import calculate_statistics, plot_category, create_report
from datasave import load_data, save_data
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.mlab import rec_append_fields,rec_join

__author__ = 'tobi'


if __name__ == '__main__':

    start = datetime(year=2013,month=9,day=1)
    database = 'data/categorized.csv'

    now = datetime.today()

    data = load_data(database)
    budget = load_budget(start)

    I = np.logical_not(data.Deleted)

    red_data,budget = calculate_statistics(data[I],start=start,budget=budget)

    save_data('figures/monthly_data.csv',red_data)

    save_data('figures/total_data.csv',budget)

    create_report(start,red_data,budget,stop=now)