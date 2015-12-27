#!/usr/bin/env python
# encoding: utf-8
"""
categories.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""
import seaborn as sns

def plot_income(ax, data, budget, category, title='Income', linecolor=sns.xkcd_rgb['medium green'], sign=1, fill_alpha=0.4):

    icategory = category.encode('utf-8')

    ax = (-sign*data[icategory]).plot(ax=ax,linewidth=2,color=linecolor,marker='o')

    ax.fill_between(data.index,-sign*data[icategory],color=linecolor,alpha=fill_alpha)

    avg = -sign*(data[icategory].mean())
    pavg = ax.axhline(avg,color='r',alpha=0.4,linewidth=2,linestyle='--',label='average')

    ax.set_title(title+' '+category)

    bud = -sign*(budget.ix[category,'Jahresbudget']/12.)

    pbud = ax.axhline(-bud,color='g',alpha=0.4,linewidth=2,linestyle='--')

    ax.legend([pavg,pbud],['Average {0:.0f} CHF'.format(avg),'Budget {0:.0f} CHF'.format(-bud)])

def plot_expense(ax, data, budget, category):

    plot_income(ax, data, budget, category,title='Expense',linecolor='#5B9ECF', sign=-1, fill_alpha=0.4)