# ----------------------------------
# project: PyCharmProjects
# file:    unittest_dataload
# author:  tobi
# created: 01.03.15
# ----------------------------------
__author__ = 'tobi'
__copyright__ = 'Copyright TobyWorks, 2015'

""""""

import unittest
import sys
from matplotlib import pyplot as plt

sys.path.append('..')

from dataload import *


class Test(unittest.TestCase):
    def test_expenses(self):

        filename = '/media/Media/Dropbox/expenses/export.csv'

        data = load_Expenses(filename)

        print data.columns

        self.assertEqual(True, False)


    def test_VisaCard(self):

        filename = '/media/Data/Eigene Dateien/Finanzen/e-Rechnungen/Visa/transaction/30.12.14.csv'

        data = load_VisaCard(filename)

        print data.columns

    def test_MasterCard(self):

        filename = '/media/Data/Eigene Dateien/Finanzen/e-Rechnungen/Mastercard/2014/Juni.pdf'

        data = load_MasterCard(filename)

        print data


if __name__ == '__main__':
    unittest.main()
