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

import unittest


class Dineral(unittest.TestCase):
    def test_import(self):
        from dineral.main import main
        #main()


    def test_mastercard(self):
        from dineral.internaldata.property import accounts
        from dineral.dataplugins.mastercard import MasterCard
        import datetime

        print(accounts())

        MasterCard._account = list(accounts().keys())[-1]
        p = MasterCard()
        print(p._account)
        data = p.load_data(datetime.date(2019, 6, 1),datetime.date(2019, 6, 30))
        data.sort_values(by=['Datum'],inplace=True,ascending=True)
        print(data)


    def test_raiffeisen(self):
        from dineral.dataplugins.raiffeisen import Raiffeisen
        import datetime

        Raiffeisen._account = 'Mietkonto Dietzingerstrasse'
        p = Raiffeisen()

        data = p.load_data(datetime.date(2019, 6, 1),datetime.date(2019, 6, 30))
        data.sort_values(by=['Datum'],inplace=True,ascending=True)
        print(data)

    def test_raiffeisen2(self):
        from dineral.dataplugins.raiffeisen import Raiffeisen
        import datetime

        Raiffeisen._account = 'Mietkonto Dietzingerstrasse'
        p = Raiffeisen()

        data = p.load_data(datetime.date(2019, 5, 1),datetime.date(2019, 5, 30))
        data.sort_values(by=['Datum'],inplace=True,ascending=True)
        print(data)





if __name__ == '__main__':
    unittest.main()
