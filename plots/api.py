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

        self._additional_plots = [Cover(),Summary(),Pie()]

    @property
    def additional_plots(self):
        return [p.name() for p in self._additional_plots]

    @property
    def plots(self):
        return self.additional_plots+self._budget.index.tolist()

    def statistics(self, window):

        db = window.database.data
        budget = window.budget.data

        date_from = window.main.report.period.dateFrom.selectedDate().toPyDate()
        date_to = window.main.report.period.dateTo.selectedDate().toPyDate()

        from statistics import calculate_monthly, calculate_summary

        self._monthly_sum = calculate_monthly(db, date_from=date_from, date_to=date_to)
        self._budget = calculate_summary(self._monthly_sum, budget, date_from=date_from, date_to=date_to)
        self._from = date_from
        self._to = date_to

    def plot(self, category, axes):

        from categories import plot

        budget = self._budget
        monthly_sum = self._monthly_sum
        date_from = self._from
        date_to = self._to

        if category in self.additional_plots:

            self._additional_plots[self.additional_plots.index(category)].plot(monthly_sum,budget,axes, date_from, date_to)

        else:

            plot(category,monthly_sum,budget,axes, date_from, date_to)

        return axes