#!/usr/bin/env python
# encoding: utf-8
"""
pie.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals

from abstract_plot import Plot

import seaborn.apionly as sns


class Pie(Plot):
    def plot(self, data, budget, ax, *args):
        import numpy as np

        I = (budget['Jahresbudget'] < 0) & (budget['Summe'] > 0)
        sizes = (budget['Summe'][I] / budget.ix[I, 'Summe'].sum())
        I2 = sizes > 0.02
        rest = 1. - sizes[I2].sum()
        sizes = sizes[I2].tolist()
        sizes.append(rest)
        # colors = sns.color_palette("Set2",len(budget)+1)
        # budget['colors']=colors[:-1]
        selected_cats = budget['Kategorie'][I][I2].tolist()
        selected_colors = budget['colors'][I][I2].tolist()

        ax.pie(sizes, explode=np.ones_like(sizes) * 0.05, autopct='%1.0f%%',
               labels=selected_cats + ['Rest'], colors=selected_colors + [sns.xkcd_rgb['light grey']],wedgeprops={'alpha':0.9})
        ax.axis('equal')
