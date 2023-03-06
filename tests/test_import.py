#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------
# project: PyCharmProjects
# file:    test_import.py
# author:  tobi
# created: 24.12.16
# ----------------------------------
__author__ = 'tobi'
__copyright__ = 'Copyright TobyWorks, 2016'

from pathlib import Path


def test_newer_postfinance_account_extract():
    from dineral.dataplugins.postfinance import PostFinance

    PostFinance._account = 'Tobias Schoch Privat'

    plugin = PostFinance()
    filename = Path("data/2022-11.pdf").resolve()
    data = plugin.load_PostFinanceExtract(str(filename))
    data

def test_import():
    from dineral.main import main
    # main()


def test_mastercard():
    from dineral.internaldata.property import accounts
    from dineral.dataplugins.mastercard import MasterCard
    import datetime

    print(accounts())

    MasterCard._account = list(accounts().keys())[-1]
    p = MasterCard()
    print(p._account)
    data = p.load_data(datetime.date(2020, 1, 1), datetime.date(2020, 1, 31))
    data.sort_values(by=['Datum'], inplace=True, ascending=True)
    print(data)


def test_raiffeisen():
    from dineral.dataplugins.raiffeisen import Raiffeisen
    import datetime

    Raiffeisen._account = 'Mietkonto Dietzingerstrasse'
    p = Raiffeisen()

    data = p.load_data(datetime.date(2019, 6, 1), datetime.date(2019, 6, 30))
    data.sort_values(by=['Datum'], inplace=True, ascending=True)
    print(data)


def test_raiffeisen2():
    from dineral.dataplugins.raiffeisen import Raiffeisen
    import datetime

    Raiffeisen._account = 'Mietkonto Dietzingerstrasse'
    p = Raiffeisen()

    data = p.load_data(datetime.date(2019, 5, 1), datetime.date(2019, 5, 30))
    data.sort_values(by=['Datum'], inplace=True, ascending=True)
    print(data)
