#!/usr/bin/env python
# encoding: utf-8
"""
categories.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""
import seaborn.apionly as sns
import matplotlib as mpl
import pandas as pd

from .defaults import monthly_settings

import logging

log = logging.getLogger(__name__)


def plot(category, data, budget, axes, date_from, date_to, mean, std):
    if (budget.ix[category, 'Jahresbudget'] > 0).squeeze():
        plot_income(axes, data, budget, category, mean, std)
    else:
        plot_expense(axes, data, budget, category, mean, std)

    monthly_settings(axes)


def plot_income(ax, data, budget, category, mean, std, title='Income', linecolor='#6ACC65', sign=1):

    icategory = category

    ax = (-sign * data[icategory]).plot(ax=ax, marker='', color=linecolor)
    ax.set_xlim(data.index[0],data.index[-1])

    if icategory in mean.columns:
        m = (-sign * mean[icategory])
        s = std[icategory].mean()

        if s>0:
            ax.fill_between(data.index, m + s, m - s, color=linecolor, alpha=0.2)
    pred = ax.plot([], [], linewidth=10, color=linecolor, alpha=0.2)[0]

    avg = -sign * (data[icategory].mean())
    # sd = data[icategory].std()
    confint = []

    c_avg = sns.xkcd_rgb['pastel red']

    pavg = ax.axhline(avg, color=c_avg, alpha=0.4, linestyle='--', label='average')

    ax.set_title(title + ' ' + category)

    bud = -sign * (budget.ix[category, 'Jahresbudget'] / 12.).squeeze()

    pbud = ax.axhline(-bud, color='g', alpha=0.4, linestyle='--')

    ax.legend([pavg, pbud, pred], ['Average {0:.0f} CHF'.format(avg), 'Budget {0:.0f} CHF'.format(-bud), 'last years'],
              loc='upper right')

    if ((-sign * data[icategory].dropna() >= 0)).all():
        ylim = ax.get_ylim()
        ax.set_ylim(0, ylim[1])
    else:
        ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)


def plot_expense(ax, data, budget, category, mean, std):
    plot_income(ax, data, budget, category, mean, std, title='Expense', linecolor='#4878CF', sign=-1)
