#!/usr/bin/env python
# encoding: utf-8
"""
expenses.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from abstract import DataPlugin
import os
import pandas as pd


class Expenses(DataPlugin):
    """ Load data from Expenses Smartphone App """

    TYPE = DataPlugin.DIR

    def load_data(self, period_from, period_to, callback=None):
        data = self.load()

        I = (data.Datum >= period_from) & (data.Datum <= period_to)
        data = data[I]

        if callback is not None:
            callback(100)

        return data

    def load(self):
        """ load data from a expenses csv file

            Parameters
            ----------
            filename:           (str) path to file to be loaded

            Returns
            -------
            pandas.Dataframe table with data, columns: date, description, amount

        """

        backup = pd.read_csv(os.path.join(self.properties, 'expenses_backup.csv'), encoding='utf-8', sep=';', quotechar="'")
        cats = pd.read_csv(os.path.join(self.properties, 'expenses_backup_categories.csv'), encoding='utf-8',sep=';', quotechar="'")
        backup = backup.merge(cats, left_on='catID', right_on='_id')
        backup = backup[['date', 'name', 'amount', 'note']].copy()
        backup.columns = ['Datum', 'Kategorie', 'Lastschrift', 'Text']

        backup.Datum = pd.DatetimeIndex(pd.to_datetime(backup.Datum)).date
        backup.Lastschrift = - backup.Lastschrift.astype(float)
        backup.sort_values('Datum', inplace=True)

        return backup
