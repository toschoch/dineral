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
import logging
import pandas as pd

log = logging.getLogger(__name__)


class Report(object):
    def __init__(self):

        self._additional_plots = [Cover(), Summary(), Pie()]

    @property
    def additional_plots(self):
        return [p.name() for p in self._additional_plots]

    @property
    def plots(self):
        return self.additional_plots + self._budget.index.tolist()

    def statistics(self, window):

        db = window.database.data
        budget = window.budget.data

        date_from = window.main.report.period.dateFrom.selectedDate().toPython()
        date_to = window.main.report.period.dateTo.selectedDate().toPython()

        from statistics import calculate_monthly, calculate_summary

        self._monthly_sum = calculate_monthly(db, date_from=date_from, date_to=date_to)
        self._budget = calculate_summary(self._monthly_sum, budget, date_from=date_from, date_to=date_to)
        self._from = date_from
        self._to = date_to

        self.predictions(db)

    def predictions(self, db):

        data = db.ix[db.Datum<self._from,['Datum', 'Kategorie', 'Lastschrift']]
        data.set_index('Datum',inplace=True,drop=True)
        data.index = pd.to_datetime(data.index)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            data = data.groupby('Kategorie').resample('1 M',how='sum').unstack(0)['Lastschrift']
        self._pred_mean = data.groupby(data.index.month).mean().fillna(0)
        self._pred_std = data.groupby(data.index.month).std().fillna(0)

    def save_statistics(self, filepath):
        import os

        year = self._from.year
        fname = os.path.join(filepath, "{}_per_month.csv".format(year))
        self._monthly_sum.to_csv(fname, sep=';', index=False)
        log.info("saved monthly data to '{}'...".format(fname))
        fname = os.path.join(filepath, "{}_summary.csv".format(year))
        self._budget.to_csv(fname, sep=';', index=False)
        log.info("saved summary to '{}'...".format(fname))

    def plot(self, category, axes):

        from categories import plot

        budget = self._budget
        monthly_sum = self._monthly_sum
        date_from = self._from
        date_to = self._to
        mean = self._pred_mean
        std = self._pred_std

        if category in self.additional_plots:

            self._additional_plots[self.additional_plots.index(category)].plot(monthly_sum, budget, axes, date_from,
                                                                               date_to, mean, std)

        else:

            plot(category, monthly_sum, budget, axes, date_from, date_to, mean, std)

        return axes
