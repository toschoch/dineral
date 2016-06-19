#!/usr/bin/env python
# encoding: utf-8
"""
categories.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""
import seaborn.apionly as sns
from defaults import monthly_settings

import logging

log = logging.getLogger(__name__)


def plot(category, data, budget, axes, date_from, date_to):
    if (budget.ix[category, 'Jahresbudget'] > 0).squeeze():
        plot_income(axes, data, budget, category)
    else:
        plot_expense(axes, data, budget, category)

    monthly_settings(axes)


def plot_income(ax, data, budget, category, title='Income', linecolor=sns.xkcd_rgb['medium green'], sign=1,
                fill_alpha=0.4):
    from scipy.stats import norm
    import matplotlib.transforms as mtransforms
    trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)

    icategory = category

    ax = (-sign * data[icategory]).plot(ax=ax, linewidth=2, color=linecolor, marker='o')

    ax.fill_between(data.index, -sign * data[icategory], color=linecolor, alpha=fill_alpha)

    avg = -sign * (data[icategory].mean())
    sd = data[icategory].std()
    confint = [norm.ppf(0.025, loc=avg, scale=sd), norm.ppf(0.975, loc=avg, scale=sd)]

    c_avg = sns.xkcd_rgb['pastel red']

    pavg = ax.axhline(avg, color=c_avg, alpha=0.4, linewidth=2, linestyle='--', label='average')
    ax.fill_between([0, 1], confint[0], confint[1], transform=trans, color=c_avg, alpha=0.1)
    ax.axhline(confint[0], color=c_avg, alpha=0.15, linewidth=1.0)
    ax.axhline(confint[1], color=c_avg, alpha=0.15, linewidth=1.0)

    ax.set_title(title + ' ' + category)

    bud = -sign * (budget.ix[category, 'Jahresbudget'] / 12.).squeeze()

    pbud = ax.axhline(-bud, color='g', alpha=0.4, linewidth=2, linestyle='--')

    ax.legend([pavg, pbud], ['Average {0:.0f} CHF'.format(avg), 'Budget {0:.0f} CHF'.format(-bud)],loc='upper right')

    if ((-sign * data[icategory].dropna() >= 0)).all():
        ylim = ax.get_ylim()
        ax.set_ylim(0, ylim[1])
    else:
        ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)


def plot_expense(ax, data, budget, category):
    plot_income(ax, data, budget, category, title='Expense', linecolor='#5B9ECF', sign=-1, fill_alpha=0.4)
