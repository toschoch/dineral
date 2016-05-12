#!/usr/bin/env python
# encoding: utf-8
"""
statistics.py

Created by Tobias Schoch on 26.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals
import pandas as pd
import datetime
import logging

log = logging.getLogger(__name__)


def calculate_monthly(data, date_from, date_to=None):
    import numpy as np
    import locale

    locale.resetlocale()

    if date_to is None:
        date_to = data.Datum.max()

    data = data[(data.Datum >= date_from) & (data.Datum <= date_to)]
    try:
        assert (data.Datum.apply(lambda x: x.year) == data.Datum.iloc[0].year).all()
    except AssertionError as err:
        log.error("Data contains entries from different year!")
        raise err

    monthly_sum = data.groupby([data.Kategorie, pd.DatetimeIndex(data.Datum, name='Month').month]).sum()
    mult_index = pd.MultiIndex.from_product([data.Kategorie.cat.categories, range(1, 13)])
    monthly_sum = monthly_sum.reindex(mult_index)

    sum_monthly = monthly_sum.Lastschrift.unstack(0)
    sum_monthly.index = pd.Series(sum_monthly.index).apply(lambda x: datetime.date(data.Datum.iloc[0].year, x, 1))

    sum_monthly = sum_monthly.fillna(0)
    sum_monthly.ix[sum_monthly.index > date_to, :] = np.nan

    return sum_monthly


def calculate_summary(data, budget, date_from, date_to):
    import numpy as np

    tolerance = 0.1

    budget['BudgetPeriode'] = budget.Jahresbudget * -(abs((date_from - date_to).days) + 1) / 365.

    Sum = data.sum()
    Sum.index = Sum.index.str.decode('utf-8')
    budget['Summe'] = Sum

    # 1==bad, 2==good, 0==neutral

    budget['GutSchlecht'] = np.logical_not(
        (((budget.Summe - budget.BudgetPeriode)) <= 0) | np.isclose(budget.Summe, budget.BudgetPeriode,
                                                                    rtol=tolerance)).astype(int)

    I2 = np.logical_not(
        ((budget.Summe - budget.BudgetPeriode) >= 0) | np.isclose(budget.Summe, budget.BudgetPeriode, rtol=tolerance))
    budget.loc[I2, 'GutSchlecht'] = 2

    a, b = budget.Summe, budget.BudgetPeriode
    second = ((a > b) & np.logical_not(np.isclose(a, b, rtol=0.01)))
    I2 = (budget.Kategorie.isin(['Steuern', 'Transport', 'Schulden', 'Vorsorge', 'Sparen']) & second)
    budget.loc[I2, 'GutSchlecht'] = 2

    second = (a < 0)
    I2 = (budget.Kategorie.isin(['Schulden', 'Vorsorge', 'Sparen']) & second)
    budget.loc[I2, 'GutSchlecht'] = 1

    a, b = budget.Summe.abs(), budget.Jahresbudget.abs()
    second = ((a > b) & np.logical_not(np.isclose(a, b, rtol=0.01)))
    I0 = (budget.Kategorie.isin(['Steuern', 'Transport']) & second)
    budget.loc[I0, 'GutSchlecht'] = 1

    budget['RelativeDifferenz'] = ((budget.Summe - budget.BudgetPeriode) / budget.BudgetPeriode)
    budget['Differenz'] = -(budget.Summe - budget.BudgetPeriode) * np.sign(budget.Jahresbudget)
    budget['TeilVomJahresbudget'] = -budget.Summe / budget.Jahresbudget

    I2 = np.lexsort((np.abs(budget['Summe']), budget['Jahresbudget'] > 0))[::-1]
    budget = budget.iloc[I2]

    return budget
