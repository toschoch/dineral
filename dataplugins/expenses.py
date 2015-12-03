#!/usr/bin/env python
# encoding: utf-8
"""
expenses.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from abstract import DataPlugin
from dateutil.parser import parse
import codecs
import pandas as pd

class Expenses(DataPlugin):
    """ Load data from Expenses Smartphone App """

    def load_data(self, period_from, period_to, callback=None):

        data=self.load_file(self.properties)

        I = (data.Datum>=period_from)&(data.Datum<=period_to)
        data=data[I]

        if callback is not None:
            callback(100)

        return data

    def load_file(self, filename):
        """ load data from a expenses csv file

            Parameters
            ----------
            filename:           (str) path to file to be loaded

            Returns
            -------
            pandas.Dataframe table with data, columns: date, description, amount

        """

        convert={
            'Date':lambda x: parse(x, dayfirst=True),
            'Amount': lambda x: -float((''.join(x.split('CHF'))).replace(',','').replace(',','.')),
            'Note': lambda x: x.strip("'")}

        # read data
        with codecs.open(filename, 'r','utf-8') as f:
            lines=f.read().splitlines()

        header=lines.pop(0).split(';')
        data=[]
        for line in lines:

            dline=[]
            for c,h in zip(line.split(';'),header):
                try:
                    dline.append(convert[h](c))
                except KeyError:
                    dline.append(c)
            data.append(dline)

        rec = pd.DataFrame(data,columns=['Datum','Kategorie','Unterkategorie','Lastschrift','Text'])
        rec.Datum = pd.DatetimeIndex(rec.Datum).date
        rec.drop('Unterkategorie',axis=1,inplace=True)
        return rec

