#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Tobias Schoch on 01.01.16.
Copyright (c) 2016. All rights reserved.
"""

from table import Summary
from pie import Pie
from cover import Cover

class Report(object):

    def __init__(self):

        self.additional_plots = [Cover(),Summary(),Pie()]

    @property
    def plot_names(self):
        return [p.name() for p in self.additional_plots]

    def plot(self, window, category, axes):

        db = window.database.data
        budget = window.budget.data

        date_from = window.main.report.period.dateFrom.selectedDate().toPyDate()
        date_to = window.main.report.period.dateTo.selectedDate().toPyDate()

        from statistics import calculate_monthly, calculate_summary
        from categories import plot


        monthly_sum = calculate_monthly(db, date_from=date_from, date_to=date_to)
        budget = calculate_summary(monthly_sum, budget, date_from=date_from, date_to=date_to)

        if category in self.plot_names:

            self.additional_plots[self.plot_names.index(category)].plot(monthly_sum,budget,axes, date_from, date_to)

        else:

            plot(category,monthly_sum,budget,axes, date_from, date_to)

        return axes