#!/usr/bin/env python
# encoding: utf-8
"""
table.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals

from .abstract_plot import Plot

import seaborn.apionly as sns


class Summary(Plot):
    def plot(self, data, budget, ax, *args):

        clr = ax.patch.get_facecolor()
        ax.set_frame_on(False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_xlim((0, 1))
        ax.set_ylim((0, 1))
        dtable = []
        columns = ['Kategorie', 'Total\n(in Periode)', 'Budget\n(in Periode)', 'Differenz\n(bez. Budget)',
                   'Abweichung\n(relativ)', '% Jahresbudget']
        for i in range(len(budget)):
            row = budget.iloc[i]
            eff = -row['Summe']
            bud_prop = -row['BudgetPeriode']

            dtable.append([row['Kategorie'], "{0:d}".format(int(eff)), "{0:d}".format(int(bud_prop)),
                           "{0:d}".format(int(row['Differenz'])), "{0:.0%}".format(row['RelativeDifferenz']),
                           "{0:.0%}".format(row['TeilVomJahresbudget'])])

        dtable.append([""] * len(columns))
        bilanz = -budget['Summe'].sum()
        income = budget[budget.Summe < 0].Summe.abs().sum()
        expense = budget[budget.Summe > 0].Summe.sum()
        dtable.append(["Einkommen:", "{0:.0f}".format(income), "Ausgaben:", "{0:.0f}".format(expense), "Bilanz:",
                       "{0:.0f}".format(bilanz)])
        table = ax.table(cellText=dtable, colLabels=columns, loc="lower center", cellLoc='center')

        ## change cell properties
        cells = table.get_celld()

        headercolor = "grey"  # "#d3d7cf"
        neutralcolor = clr
        goodcolor = sns.xkcd_rgb['medium green']
        badcolor = sns.xkcd_rgb['pale red']

        for i in range(len(columns)):
            cell = cells[0, i]
            cell.set_facecolor(headercolor)
            cell.set_alpha(0.4)
            cell.set_height(0.07)
            cell.set_lw(0.1)
            cell.set_fontsize(15)

        for j in range(1, len(budget) + 1):

            goodbad = budget.GutSchlecht.iloc[j - 1]
            if goodbad == 1:
                color = badcolor
            elif goodbad == 2:
                color = goodcolor
            else:
                color = neutralcolor

            for i in range(len(columns)):
                cell = cells[j, i]
                cell.set_facecolor(color)
                cell.set_alpha(0.4)
                cell.set_lw(0.3)

        for i in range(len(columns)):
            cell = cells[len(dtable) - 1, i]
            cell.set_lw(0)

        for i in range(len(columns)):
            cell = cells[len(dtable), i]
            if i % 2 == 0:
                cell.set_facecolor(headercolor)
            else:
                cell.set_facecolor(neutralcolor)
            if i == len(columns) - 1:
                if bilanz < 0:
                    cell.set_facecolor(badcolor)
                else:
                    cell.set_facecolor(goodcolor)

            cell.set_alpha(0.4)
            cell.set_lw(0.3)
