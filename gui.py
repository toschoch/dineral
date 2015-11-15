#!/usr/bin/env python
# encoding: utf-8
"""
gui.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtCore import Qt, QModelIndex, QDate

import pandas as pd
from qtpandas import DataFrameWidget
from datacollect import load_budget, load_data, load_database

import pandas as pd

clf_file = 'data/classifier.pickle'

class DateRange(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)

        self.dateFrom = QtW.QCalendarWidget(self)
        self.dateTo = QtW.QCalendarWidget(self)

        self.initUI()


    def initUI(self):
        grp = QtW.QGroupBox("Period:",self)
        layout = QtW.QGridLayout(self)

        layout.addWidget(QtW.QLabel("From",self),0,0)
        layout.addWidget(self.dateFrom,1,0)
        layout.addWidget(QtW.QLabel("To",self),0,1)
        layout.addWidget(self.dateTo,1,1)
        grp.setLayout(layout)

        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)

class FinanceDataSources(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self,parent)

        self.expenses = QtW.QCheckBox("Expenses",self)
        self.expenses.setChecked(True)
        self.mastercard = QtW.QCheckBox("MasterCard",self)
        self.mastercard.setChecked(True)
        self.postfinance = QtW.QCheckBox("PostFinance",self)
        self.postfinance.setChecked(True)


        self.initUI()

    def initUI(self):
        grp = QtW.QGroupBox("Import from:",self)
        layout = QtW.QHBoxLayout(self)
        layout.addWidget(self.expenses)
        layout.addWidget(self.mastercard)
        layout.addWidget(self.postfinance)
        grp.setLayout(layout)

        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)



class FinanceDataImport(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self,parent)

        self.period = DateRange(self)
        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),today.month()-1,1))
        self.period.dateTo.setSelectedDate(QDate(today.year(),today.month()-1,QDate(today.year(),today.month()-1,1).daysInMonth()))
        self.sources = FinanceDataSources(self)

        self.btnImport = QtW.QPushButton("Import",self)
        self.btnImport.clicked.connect(self.dataImport)

        self.imported_data = None


        self.initUI()

    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        layout.addWidget(self.sources)

        row = QtW.QHBoxLayout(self)
        row.addStretch(1)
        row.addWidget(self.btnImport)
        layout.addLayout(row)

        self.setLayout(layout)

    def dataImport(self):


        start = self.period.dateFrom.selectedDate().toPyDate()
        stop = self.period.dateTo.selectedDate().toPyDate()

        from datacollect import load_budget, load_Expenses_from_Dropbox, load_MasterCardData, load_PostFinanceData, expand_EFinance

        main = self.parent().parent().parent()

        data = []
        callback=lambda x:main.progress.setValue(int(x))

        if self.sources.expenses.isChecked():
            data.append(load_Expenses_from_Dropbox(start,stop))

        if self.sources.postfinance.isChecked():
            main.status.showMessage("load data from PostFinance extracts... Please wait one moment!")
            data.append(load_PostFinanceData(start,stop,callback=callback))

        if self.sources.mastercard.isChecked():
            callback(0)
            main.status.showMessage("load data from MasterCard extracts... Please wait one moment!")
            data.append(load_MasterCardData(start,stop,callback=callback))

        data = pd.concat(data,axis=0)
        data = expand_EFinance(data)
        data.set_index('Datum',drop=False,inplace=True)
        data.sort(inplace=True)
        data.reset_index(inplace=True,drop=True)

        budget = load_budget(start=start,stop=stop)

        import numpy as np
        data.drop('Unterkategorie',axis=1,inplace=True)
        data.Kategorie = pd.Categorical([np.NaN]*data.shape[0],categories=budget.Kategorie.tolist())


        data=data[['Datum','Text','Lastschrift','Kategorie']]

        self.imported_data = data

        hashes = self.create_hashes(data)
        db = load_database(budget.Kategorie.tolist())

        I = hashes.isin(db.Hash)
        data['in database']=I

        self.table = TransactionTable(data,parent=self)
        self.table.show()

    @staticmethod
    def create_hashes(data):

        import hashlib
        from unidecode import unidecode

        def hash(row):
            h = hashlib.md5(unidecode(row['Datum'].strftime('%d-%m-%Y').decode('utf-8'))+' '+unidecode(row['Text'])+' '+'CHF {0:.0f}'.format(row['Lastschrift'])).hexdigest()
            return pd.Series({'Hash':h})

        return data.apply(hash,axis=1).Hash


class FinanceReport(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self,parent)
        self.period = DateRange(self)
        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),1,1))
        self.initUI()

    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        layout.addStretch(1)
        self.setLayout(layout)

class TransactionTable(DataFrameWidget):

    def __init__(self, data, parent=None):

        DataFrameWidget.__init__(self, data)
        i_cat = data.columns.tolist().index('Kategorie')
        self.dataTable.setCurrentIndex(self.dataModel.index(0,i_cat))
        self.dataTable.setColumnWidth(i_cat,200)
        h = self.getMaxColumnHeight()
        for i in range(self.dataModel.rowCount()):
            self.dataTable.setRowHeight(i,h)
        self.setFixedWidth(self.getWidth())
        self.setMinimumHeight(400)

        self.setWindowTitle('Transactions')


class FinanceMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.progress = QtW.QProgressBar(self)
        self.progress.setRange(0,100)
        self.status = self.statusBar()
        self.status.addPermanentWidget(self.progress)
        self.initUI()

    def initUI(self):
        self.status.showMessage("Ready")

        self.setWindowTitle('MyFinance')
        self.tab = QtW.QTabWidget(self)
        self.tab.addTab(FinanceDataImport(self), "Import")
        self.tab.addTab(FinanceReport(self),"Report")

        self.setCentralWidget(self.tab)