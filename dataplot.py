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

def calculate_statistics(data, start=None, stop=None, months=12, budget=None):

    if start is None:
        start = np.min(data['Datum'])
        start = firstOf('month',start)
    if stop is None:
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


        budget = rec_append_fields(budget,'GutSchlecht',np.logical_or((budget.Summe-budget.BudgetPeriode)>=0,np.allclose(budget.Summe,budget.BudgetPeriode,atol=0.5)))
        budget = rec_append_fields(budget,'RelativeDifferenz',(budget.Summe-budget.BudgetPeriode)/budget.BudgetPeriode)
        budget = rec_append_fields(budget,'Differenz',(budget.Summe-budget.BudgetPeriode)*np.sign(budget['Jahresbudget']))
        budget = rec_append_fields(budget,'TeilVomJahresbudget',budget.Summe/budget.Jahresbudget)

        I2=np.lexsort((-budget['Summe'],budget['Jahresbudget']>0))[::-1]
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

    # Ausgaben
    if budget['Jahresbudget'][budget.Kategorie==category] < 0:

        linecolor='#5B9ECF'
        plt.plot(category_data.Datum,category_data.Total,linewidth=2,color=linecolor,marker='o')

        plt.fill_between(category_data.Datum,category_data.Total,color=linecolor,alpha=0.6)

        pavg, =plt.plot(category_data.Datum,np.repeat(avg,len(category_data)),color='r',alpha=0.4,linewidth=2,linestyle='--')

        plt.title('Ausgaben '+category)
        if budget is not None:

            pbud, =plt.plot(category_data.Datum,np.repeat(-bud,len(category_data)),color='g',alpha=0.4,linewidth=2,linestyle='--')
            plt.legend([pavg,pbud],['Durchschnitt {0:.0f} CHF'.format(avg),'Budget {0:.0f} CHF'.format(-bud)],prop=fp)
        else:
            plt.legend([pavg],['Durchschnitt {0:.0f} CHF'.format(avg)],prop=fp)

    # Einkommen
    else:

        linecolor='#95D444'

        plt.plot(category_data.Datum,-category_data.Total,linewidth=2,color=linecolor,marker='o')

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
    if ylim[0] < 0:
        ylim = (ylim[0]*1.2,ylim[1]*1.2)
    else:
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
        text+= start.strftime('%d. %B %Y').decode('utf-8')
        text+= " bis "
        text+= stop.strftime(u'%d. %B %Y').decode('utf-8')
        dtable = []
        columns = ['Kategorie','Total\n(in Periode)','Budget\n(in Periode)','Differenz\n(bez. Budget)','Abweichung\n(relativ)','% Jahresbudget']
        for row in budget:
            eff = row['Summe']
            bud_year = row['Jahresbudget']
            bud_prop = row['BudgetPeriode']

            dtable.append([row['Kategorie'],"{0:d}".format(int(eff)),"{0:d}".format(int(bud_prop)),
                          "{0:d}".format(int(row['Differenz'])),"{0:.0%}".format(row['RelativeDifferenz']),
                          "{0:.0%}".format(row['TeilVomJahresbudget'])])


        dtable.append([""]*len(columns))
        bilanz = sum(budget['Summe'])
        dtable.append(["Einkommen:","{0:.0f}".format(sum(budget['Summe'][budget['Summe']>0])),"Ausgaben:","{0:.0f}".format(sum(budget['Summe'][budget['Summe']<=0])),"Bilanz:","{0:.0f}".format(bilanz)])
        # colwidths = [.25,0.2,0.2,0.2,0.2,0.2]
        table=plt.table(cellText=dtable,colLabels=columns,loc="lower center",cellLoc='center')#,colWidths=colwidths)
        plt.text(0.5,0.97,text,transform=plt.gca().transAxes,horizontalalignment='center',verticalalignment="bottom")

        ## change cell properties
        cells = table.get_celld()

        headercolor = "grey" #"#d3d7cf"
        goodcolor = "yellow"#"#FDFD96"
        badcolor = "red"#"#d75040"
        for i in range(len(columns)):
            cell = cells[0,i]
            cell.set_facecolor(headercolor)
            cell.set_alpha(0.4)
            cell.set_height(0.07)
            cell.set_lw(0.1)
            cell.set_fontsize(15)

        for j in range(1,len(budget)+1):

            if budget['GutSchlecht'][j-1]:
                color = goodcolor
            else:
                color = badcolor

            for i in range(len(columns)):
                cell = cells[j,i]
                cell.set_facecolor(color)
                cell.set_alpha(0.4)
                cell.set_lw(0.3)

        for i in range(len(columns)):
            cell = cells[len(dtable)-1,i]
            cell.set_lw(0)

        for i in range(len(columns)):
            cell = cells[len(dtable),i]
            if i%2==0:
                cell.set_facecolor(headercolor)
            else:
                cell.set_facecolor(goodcolor)
            if i==len(columns)-1 and bilanz<0:
                cell.set_facecolor(badcolor)

            cell.set_alpha(0.4)
            cell.set_lw(0.3)

        pdf.savefig()

        # make category plots
        for category in budget['Kategorie']:
            plot_category(category,data,budget)
            pdf.savefig()