#!/usr/bin/env python
# encoding: utf-8
"""
statistics.py

Created by Tobias Schoch on 26.12.15.
Copyright (c) 2015. All rights reserved.
"""
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
    from dateutil.relativedelta import relativedelta

    budget['BudgetPeriode'] = budget.Jahresbudget * relativedelta(date_from,date_to).months / 12

    budget['Summe'] = data.sum()

    budget['GutSchlecht'] = (((budget.Summe-budget.BudgetPeriode)>=0) | np.isclose(budget.Summe,budget.BudgetPeriode,rtol=0.01)).astype(int)

    a, b = budget.Summe.abs(), budget.Jahresbudget.abs()
    second = ((a>=b) & np.logical_not(np.isclose(a,b,rtol=0.01)))
    I2 = (budget.Kategorie.isin(['Lohn','Schulden','Vorsorge','Sparen','Steuern']) & second)
    budget.loc[I2,'GutSchlecht'] = 2

    I0 = (budget.Kategorie.isin(['Steuern','Transport']) & second)
    budget.loc[I0,'GutSchlecht'] = 0

    budget['RelativeDifferenz'] = ((budget.Summe-budget.BudgetPeriode)/budget.BudgetPeriode)
    budget['Differenz'] = (budget.Summe-budget.BudgetPeriode)*np.sign(budget.Jahresbudget)
    budget['TeilVomJahresbudget'] = budget.Summe/budget.Jahresbudget

    return budget
