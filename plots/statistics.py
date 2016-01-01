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


def calculate_monthly(data, date_from, date_to=None):

    import numpy as np
    import locale

    locale.resetlocale()

    if date_to is None:
        date_to = data.Datum.max()

    data = data[data.Datum>=date_from]
    assert (data.Datum.apply(lambda x: x.year)==data.Datum.iloc[0].year).all()

    monthly_sum = data.groupby([data.Kategorie,pd.DatetimeIndex(data.Datum,name='Month').month]).sum()
    mult_index = pd.MultiIndex.from_product([data.Kategorie.cat.categories,range(1,13)])
    monthly_sum = monthly_sum.reindex(mult_index)

    sum_monthly = monthly_sum.Lastschrift.unstack(0)
    sum_monthly.index = pd.Series(sum_monthly.index).apply(lambda x: datetime.date(data.Datum.iloc[0].year,x,1))

    sum_monthly = sum_monthly.fillna(0)
    sum_monthly.ix[sum_monthly.index>date_to,:]=np.nan

    return sum_monthly

def calculate_summary(data, budget, date_from, date_to):

    import numpy as np

    budget['BudgetPeriode'] = budget.Jahresbudget * ((date_from-date_to).days+1)/365.

    Sum = data.sum()
    Sum.index = Sum.index.str.decode('utf-8')
    budget['Summe'] = Sum

    budget['GutSchlecht'] = np.logical_not((((budget.Summe-budget.BudgetPeriode))<=0) | np.isclose(budget.Summe,budget.BudgetPeriode,rtol=0.02)).astype(int)

    I2 = np.logical_not(((budget.Summe-budget.BudgetPeriode)>=0) | np.isclose(budget.Summe,budget.BudgetPeriode,rtol=0.02))
    budget.loc[I2,'GutSchlecht']=2

    a, b = budget.Summe, budget.BudgetPeriode
    second = ((a>b) & np.logical_not(np.isclose(a,b,rtol=0.01)))
    I2 = (budget.Kategorie.isin(['Steuern','Transport','Schulden','Vorsorge','Sparen']) & second)
    budget.loc[I2,'GutSchlecht'] = 2

    a, b = budget.Summe.abs(), budget.Jahresbudget.abs()
    second = ((a>b) & np.logical_not(np.isclose(a,b,rtol=0.01)))
    I0 = (budget.Kategorie.isin(['Steuern','Transport']) & second)
    budget.loc[I0,'GutSchlecht'] = 1

    budget['RelativeDifferenz'] = ((budget.Summe-budget.BudgetPeriode)/budget.BudgetPeriode)
    budget['Differenz'] = -(budget.Summe-budget.BudgetPeriode)*np.sign(budget.Jahresbudget)
    budget['TeilVomJahresbudget'] = -budget.Summe/budget.Jahresbudget

    I2=np.lexsort((budget['Summe'],budget['Jahresbudget']>0))[::-1]
    budget = budget.iloc[I2]

    return budget
