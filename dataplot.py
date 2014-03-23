# -- coding: utf-8 --
from dateutil import rrule
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.font_manager import FontProperties
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from unidecode import unidecode
from utils import firstOf, lastOf

__author__ = 'tobi'

def calculate_statistics(data):

    start = np.min(data['Datum'])
    stop = np.max(data['Datum'])

    base = firstOf('month',start-relativedelta(months=1))
    start = lastOf('month',base)
    stop = firstOf('month',stop+relativedelta(months=1))

    # find data
    rr = rrule.rrule(rrule.MONTHLY,dtstart=base)
    months = rr.between(start,stop)

    data_reduced=[]
    for category in np.unique(data.Kategorie):
        # select category
        category_data = data[data.Kategorie==category]

        for month in months:

            I = np.logical_and(category_data.Datum>=month,category_data.Datum<(month+relativedelta(months=1)))
            data_reduced.append([month,np.sum(category_data.Lastschrift[I]),category])


    rec = np.rec.fromrecords(data_reduced,names=['Datum','Total','Kategorie'])
    rec.sort(order='Datum')
    return rec




def plot_category(category,data,budget):
    """ creates a plot for category
    """
    category_data = data[data.Kategorie==unidecode(category)]


    fh = plt.figure()
    avg = np.mean(category_data.Total)
    if avg > 0:
        linecolor='#5B9ECF'
        plt.plot(category_data.Datum,category_data.Total,linewidth=2,color=linecolor,marker='o')
        plt.fill_between(category_data.Datum,category_data.Total,color=linecolor,alpha=0.6)
        pavg, =plt.plot(category_data.Datum,np.repeat(avg,len(category_data)),color='r',alpha=0.4,linewidth=2,linestyle='--')
        plt.title('Ausgaben '+category)
    else:
        linecolor='#95D444'
        plt.plot(category_data.Datum,category_data.Total,linewidth=2,color=linecolor,marker='o')
        plt.fill_between(category_data.Datum,-category_data.Total,color=linecolor,alpha=0.6)
        pavg, =plt.plot(category_data.Datum,-np.repeat(avg,len(category_data)),color='r',alpha=0.4,linewidth=2,linestyle='--')
        plt.title('Einkommen'+category)

    plt.grid()
    fp = FontProperties(size='medium')
    plt.legend([pavg],['Durchschnitt {0:.0f} CHF'.format(avg)],prop=fp)
    fmt = DateFormatter('%b/%Y')
    loc = DayLocator(bymonthday=1)
    ax = plt.gca()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)
    plt.xticks(rotation=20)
    plt.ylabel('Total Monat [CHF]')

    ylim = plt.ylim()
    ylim = (0,ylim[1]*1.2)
    plt.ylim(ylim)

    return fh

