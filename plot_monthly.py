# -- coding: utf-8 --

import matplotlib
matplotlib.use("Qt4Agg")
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datacollect import load_budget
from dataplot import calculate_statistics,  create_report
from datasave import load_data, save_data
from utils import lastOf, firstOf
import numpy as np
import matplotlib.pyplot as plt
import os

from datacollect import dropbox_path

__author__ = 'tobi'


if __name__ == '__main__':

    start = firstOf('year',datetime.now())
    database = 'data/categorized.csv'

    now = lastOf('month',datetime.now())-relativedelta(months=1)

    data = load_data(database)
    budget = load_budget(start,stop=now)

    I = np.logical_not(data.Deleted)

    red_data,budget = calculate_statistics(data[I],start=start, stop=now,budget=budget)

    save_data('figures/monthly_data.csv',red_data)

    save_data('figures/total_data.csv',budget)

    create_report(start,red_data,budget,stop=now,output=os.path.join(os.path.join('/media/Media/Dropbox/finance'),'report.pdf'))

    plt.close()