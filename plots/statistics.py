#!/usr/bin/env python
# encoding: utf-8
"""
statistics.py

Created by Tobias Schoch on 26.12.15.
Copyright (c) 2015. All rights reserved.
"""
import pandas as pd
import datetime


def calculate_monthly(data):

    import calendar
    import numpy as np
    import locale

    locale.resetlocale()

    monthly_sum = data.groupby([data.Kategorie,pd.DatetimeIndex(data.Datum,name='Month').month]).sum()
    mult_index = pd.MultiIndex.from_product([data.Kategorie.cat.categories,range(1,13)])
    monthly_sum = monthly_sum.reindex(mult_index)

    sum_monthly = monthly_sum.Lastschrift.unstack(0)
    sum_monthly.index = pd.Series(sum_monthly.index).apply(lambda x: datetime.date(data.Datum.iloc[0].year,x,1))

    sum_monthly = sum_monthly.fillna(0)
    sum_monthly.ix[sum_monthly.index>data.Datum.max(),:]=np.nan

    return sum_monthly