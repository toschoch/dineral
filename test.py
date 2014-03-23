# -- coding: utf-8 --
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule
import datetime
from unidecode import unidecode
from datacollect import load_Expenses_from_phone
from dataload import *
from dataplot import calculate_statistics, plot_category
from datasave import load_data, load_categories
from utils import firstOf, lastOf
import matplotlib.pyplot as plt

__author__ = 'tobi'



if __name__ == '__main__':

    categories = load_categories('categories.txt')
    data = load_data(ur'categorized.csv')
    # print load_MasterCardExtract(ur'/home/tobi/Finance/e-Rechnungen/Mastercard/2014/Februar.pdf')

    red_data = calculate_statistics(data)
    print [c[0] for c in categories]



    cats=np.unique(red_data.Kategorie)
    for category,desc in categories:
        if unidecode(category) not in cats: continue
        print unidecode(category)
        plot_category(category,red_data,None)
        plt.savefig('figures/'+category.replace('/','-')+'.pdf')


