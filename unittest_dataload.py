__author__ = 'tobi'

from dataload import *
import unittest

class MyTestCase(unittest.TestCase):
    def test_MasterCardExtract(self):
        """ Test loading Master Card Extract
        """
        load_MasterCardExtract(r'Januar.txt')


    def test_VisaCardTransaction(self):
        """ Test loading Visa Card Transaction
        """
        load_VisaCardTransaction(r'23.01.14.csv')

    def test_PostFinanceExtract(self):
        """ Test loading Post Finance Extract
        """
        load_PostFinanceExtract(r'2014-01.txt')


if __name__ == '__main__':
    unittest.main()
