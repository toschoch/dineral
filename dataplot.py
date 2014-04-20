# -- coding: utf-8 --
from datetime import datetime
from dateutil import rrule
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.font_manager import FontProperties
from matplotlib.mlab import rec_append_fields, rec_join
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from unidecode import unidecode
from utils import firstOf, lastOf

__author__ = 'tobi'

def calculate_statistics(data, start=None, months=12, budget=None):

    if start is None:
        start = np.min(data['Datum'])
        start = firstOf('month',start)
    stop = np.max(data['Datum'])

    # find data
    rr = rrule.rrule(rrule.MONTHLY,dtstart=start,count=months)
    mths = list(rr)

    data_reduced=[]
    for category in np.unique(data.Kategorie):
        # select category
        category_data = data[data.Kategorie==category]

        for month in mths:

            I = np.logical_and(category_data.Datum>=month,category_data.Datum<(month+relativedelta(months=1)))
            if month<stop:
                data_reduced.append([month,np.sum(category_data.Lastschrift[I]),category])
            else:
                data_reduced.append([month,np.nan,category])


    rec = np.rec.fromrecords(data_reduced,names=['Datum','Total','Kategorie'])
    rec.sort(order='Datum')

    # calculate with budget
    if budget is not None:

        Sum=[]
        for category in rec.Kategorie:
            Sum.append([category,-np.nansum(rec.Total[rec.Kategorie==category])])
        Sum = np.rec.fromrecords(Sum,names=['Kategorie','Summe'])

         # append procentual budget
        b = budget.Jahresbudget*(relativedelta(datetime.today(),start).months/12.)

        budget = np.rec.fromarrays([budget.Kategorie,budget.Jahresbudget,b],names=['Kategorie','Jahresbudget','BudgetPeriode'])

        budget = rec_join('Kategorie',Sum,budget)

        budget = rec_append_fields(budget,'Differenz',np.abs(budget.Summe)-np.abs(budget.BudgetPeriode))
        budget = rec_append_fields(budget,'RelativeDifferenz',budget.Differenz/np.abs(budget.BudgetPeriode))
        budget = rec_append_fields(budget,'TeilVomJahresbudget',np.abs(budget.Summe)/np.abs(budget.Jahresbudget))

        I2=np.argsort(np.abs(budget['Summe']))[::-1]
        budget = budget[I2]

        return rec, budget

    else:
        return rec


def plot_category(category,data,budget=None):
    """ creates a plot for category
    """
    category_data = data[data.Kategorie==category]


    fh = plt.figure()
    avg = np.nanmean(category_data.Total)
    if budget is not None:
        bud = float(budget['Jahresbudget'][budget.Kategorie==category][0])/12.
    fp = FontProperties(size='medium')
    if avg > 0:
        linecolor='#5B9ECF'
        plt.plot(category_data.Datum,category_data.Total,linewidth=2,color=linecolor,marker='o')
        plt.fill_between(category_data.Datum,category_data.Total,color=linecolor,alpha=0.6)
        pavg, =plt.plot(category_data.Datum,np.repeat(avg,len(category_data)),color='r',alpha=0.4,linewidth=2,linestyle='--')
        plt.title('Ausgaben '+category)
        if budget is not None:
            pbud, =plt.plot(category_data.Datum,np.repeat(bud,len(category_data)),color='g',alpha=0.4,linewidth=2,linestyle='--')
            plt.legend([pavg,pbud],['Durchschnitt {0:.0f} CHF'.format(avg),'Budget {0:.0f} CHF'.format(bud)],prop=fp)
        else:
            plt.legend([pavg],['Durchschnitt {0:.0f} CHF'.format(avg)],prop=fp)
    else:
        linecolor='#95D444'
        plt.plot(category_data.Datum,category_data.Total,linewidth=2,color=linecolor,marker='o')
        plt.fill_between(category_data.Datum,-category_data.Total,color=linecolor,alpha=0.4)
        pavg, =plt.plot(category_data.Datum,-np.repeat(avg,len(category_data)),color='r',alpha=0.4,linewidth=2,linestyle='--')
        plt.title('Einkommen '+category)
        if budget is not None:
            pbud, =plt.plot(category_data.Datum,np.repeat(bud,len(category_data)),color='g',alpha=0.4,linewidth=2,linestyle='--')
            plt.legend([pavg,pbud],['Durchschnitt {0:.0f} CHF'.format(-avg),'Budget {0:.0f} CHF'.format(bud)],prop=fp)
        else:
            plt.legend([pavg],['Durchschnitt {0:.0f} CHF'.format(-avg)],prop=fp)

    plt.grid()
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

def create_report(start,data,budget,stop=datetime.today(),output='figures/report.pdf'):
    """ creates and saves a pdf report """

    with PdfPages(output) as pdf:

        # summarize
        plt.figure()
        ax = plt.gca()
        ax.set_frame_on(False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        plt.xlim((0,1))
        plt.ylim((0,1))
        text = u"Report MyFinance\n\n"
        text+= u"Periode: \n"
        text+= start.strftime('%d. %B %Y').decode('utf-8')
        text+= " bis "
        text+= stop.strftime(u'%d. %B %Y').decode('utf-8')
        table = []
        for row in budget:
            eff = row['Summe']
            bud_year = row['Jahresbudget']
            bud_prop = row['BudgetPeriode']

            table.append([row['Kategorie'],"{0:d}".format(int(eff)),"{0:d}".format(int(bud_prop)),
                          "{0:d}".format(int(row['Differenz'])),"{0:.0%}".format(row['RelativeDifferenz']),
                          "{0:.0%}".format(row['TeilVomJahresbudget'])])
        columns = ['Kategorie','Total','Budget','Differenz','Abweichung','% Jahresbudget']
        # colwidths = [.25,0.2,0.2,0.2,0.2,0.2]
        plt.table(cellText=table,colLabels=columns,loc="lower center",cellLoc='center')#,colWidths=colwidths)
        plt.text(0.5,0.9,text,transform=plt.gca().transAxes,horizontalalignment='center')
        pdf.savefig()

        # make category plots
        for category in budget['Kategorie']:
            plot_category(category,data,budget)
            pdf.savefig()