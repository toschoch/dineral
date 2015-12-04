#!/usr/bin/env python
# encoding: utf-8
"""
gui.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QModelIndex, QDate, QThread

import pandas as pd
from qttransactiontable import TransactionTable
from qtpandas import DataFrameWidget
from qtutils import QDateRange, QCheckBoxGroup
from qtimport import DataImport

import pandas as pd

clf_file = 'data/classifier.pickle'


class FinanceDataImport(QWidget):

    def __init__(self, plugins, parent):
        QWidget.__init__(self,parent)

        self.period = QDateRange(self)
        self.sources = QCheckBoxGroup([d.name() for d in plugins],'Import from:',self)
        self.btnImport = QtW.QPushButton("Import",self)
        self.importer = DataImport(plugins,parent=self)

        self.importer.success.connect(self.showData)
        self.btnImport.clicked.connect(self.importData)

        self.initUI()

        self.setStartDate()

    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        layout.addWidget(self.sources)
        layout.addStretch(1)

        row = QtW.QHBoxLayout(self)
        row.addStretch(1)
        row.addWidget(self.btnImport)
        layout.addLayout(row)

        self.setLayout(layout)

    def setStartDate(self):

        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),today.month()-1,1))
        self.period.dateTo.setSelectedDate(QDate(today.year(),today.month()-1,QDate(today.year(),today.month()-1,1).daysInMonth()))

    # def save_imported(self, data):
    #     data.Datum = pd.to_datetime(data.Datum)
    #     self.imported_data.Datum = pd.to_datetime(self.imported_data.Datum)
    #     self.imported_data.ix[data.index,data.columns]=data
    #     msg = "{} transaction imported".format(data.shape[0])
    #     self.main.status.showMessage(msg)
    #
    #     from datacollect import save_database
    #     imported_data = self.imported_data.set_index('Hash',drop=False)
    #     imported_data.drop('Database',axis=1,inplace=True)
    #     imported_data.Kategorie = pd.Categorical(imported_data.Kategorie,categories=self.budget.Kategorie.tolist())
    #     self.db = imported_data.combine_first(self.db)
    #     self.db.sort('Datum',inplace=True)
    #     save_database(self.db)
    #
    #
    def importData(self):

        start = self.period.dateFrom.selectedDate().toPyDate()
        stop = self.period.dateTo.selectedDate().toPyDate()

        self.selectedPeriod = (start,stop)

        for check,plugin in zip(self.sources.checkboxes,self.importer.plugins):
            plugin.LOAD = check.isChecked()

        self.importer.start(start,stop)

    def showData(self, data):

        start, stop = self.selectedPeriod

        print data
        #
        # from datacollect import load_budget
        # budget = load_budget(start=start,stop=stop)
        # self.budget = budget
        #
        # import numpy as np
        # data.Kategorie = pd.Categorical([np.NaN]*data.shape[0],categories=budget.Kategorie)
    #
    #     hashes = self.create_hashes(data)
    #     db = load_database(budget.Kategorie.tolist())
    #     db.set_index('Hash',inplace=True,drop=False)
    #
    #     self.db = db
    #
    #     in_db = hashes.isin(db.index)
    #     data['Database']=in_db
    #     data['Deleted']=False
    #     data.set_index(hashes,inplace=True)
    #
    #     joined=data.join(db,how='inner',lsuffix='_data')[['Kategorie','Deleted']]
    #     data.ix[joined.index,['Kategorie','Deleted']]=joined
    #
    #     data=data[['Datum','Text','Lastschrift','Database','Deleted','Kategorie']]
    #     data.reset_index(inplace=True)
    #
    #     self.imported_data = data
    #
    #     # categorize
    #     import pickle, os
    #     if os.path.isfile(clf_file):
    #         with open(clf_file,'rb') as fp:
    #             clf = pickle.load(fp)
    #
    #     classes = pd.Series(clf.classes_names,name='Kategorie')
    #     I = ~in_db
    #     if I.any():
    #         prediction = classes[clf.predict(data[I].Text)]
    #         data.loc[I,'Deleted'] = (prediction == 'Delete').values
    #         guessed = pd.Categorical(prediction,categories=classes)
    #
    #         data.Kategorie = pd.Categorical(data.Kategorie,classes)
    #         data.loc[I,'Kategorie'] = guessed
    #
    #     data.loc[data.Deleted,'Kategorie']=np.nan
    #     data.Kategorie = pd.Categorical(data.Kategorie,self.budget.Kategorie.tolist())
    #
    #     self.main.status.clearMessage()
    #     self.main.progress.setValue(0)
    #
    #     self.main.centralWidget().content.addWidget(TransactionTable(data.loc[:,['Datum','Text','Lastschrift','Database','Deleted','Kategorie']],self))

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
        self.period = QDateRange(self)
        self.buttonReport = QtW.QPushButton("Create Report",self)
        self.buttonReport.clicked.connect(self.createReport)

        self.initUI()

        self.setStartDate()

    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        layout.addStretch(1)
        row = QtW.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.buttonReport)
        layout.addLayout(row)
        self.setLayout(layout)

    def setStartDate(self):
        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),1,1))

    def createReport(self):
        return
        # import calendar
        # import numpy as np
        #
        # self.main = self.parent().parent().parent().parent()
        #
        # start = self.period.dateFrom.selectedDate().toPyDate()
        # stop = self.period.dateTo.selectedDate().toPyDate()
        # budget = load_budget(start,stop)
        #
        # db = load_database(budget.Kategorie.tolist())
        # db.drop(db.Deleted,axis=0,inplace=True)
        # db.drop('Deleted',axis=1,inplace=True)
        #
        # db = db[(db.Datum>=start)&(db.Datum<=stop)]
        #
        #
        # empty = pd.DataFrame(0,index=pd.MultiIndex.from_product([budget.Kategorie.tolist(),range(1,12)],names=['Kategorie','Month']),columns=['Total'])
        # print empty
        #
        # monthly_sum = db.groupby([lambda i: db.ix[i,'Kategorie'],lambda i: db.ix[i,'Datum'].month]).sum()
        #
        # print empty.combine_first(monthly_sum)

# class DataImporter(QThread):
#
#     def __init__(self, plugins, checked, parent=None):
#
#         QThread.__init__(self, parent=parent)
#
#         self.plugins = plugins
#         self.checked = checked
#
#     def run(self):
#
#         start, stop = self.start_date,self.stop_date
#         main = self.main
#
#         progress = QtW.QProgressDialog(self.parent())
#         progress.setWindowTitle("Import Data")
#
#         data = []
#         for plugin,checked in zip(self.plugins,self.checked):
#             if checked:
#                 try:
#                     progress.setLabelText(plugin.description())
#                     d = plugin.load(start,stop)
#                     data.append(d)
#                 except:
#                     pass
#
#         # Merge data
#         # data = pd.concat(data,axis=0)
#         # data = expand_EFinance(data)
#         # data.set_index('Datum',drop=False,inplace=True)
#         # data.sort(inplace=True)
#         # data.reset_index(inplace=True,drop=True)
#
#         self.data = data