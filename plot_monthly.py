# -- coding: utf-8 --
from unidecode import unidecode
from dataplot import calculate_statistics, plot_category
from datasave import load_categories, load_data
import numpy as np
import matplotlib.pyplot as plt


__author__ = 'tobi'


if __name__ == '__main__':

    categories = load_categories('categories.txt')
    data = load_data(ur'categorized.csv')
    # print load_MasterCardExtract(ur'/home/tobi/Finance/e-Rechnungen/Mastercard/2014/Februar.pdf')

    red_data = calculate_statistics(data)

    cats=np.unique(red_data.Kategorie)
    for category,desc in categories:
        if unidecode(category) not in cats: continue
        print unidecode(category)
        plot_category(category,red_data,None)
        plt.savefig('figures/'+category.replace('/','-')+'.pdf')