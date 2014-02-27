__author__ = 'tobi'

from dataload import load_PostFinanceExtract,load_MasterCardExtract,load_VisaCardTransaction

if __name__=='__main__':
    print load_PostFinanceExtract(r'2014-01.txt')
    print load_MasterCardExtract(r'Januar.txt')
    print load_VisaCardTransaction(r'23.01.14.csv')