#!/usr/bin/env python
# encoding: utf-8
"""
gui.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtCore import Qt, QModelIndex, QDate, QThread
from PyQt5.QtGui import QIcon

import pandas as pd
from transactiontable import TransactionTable
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

    def save_imported(self, data):
        data.Datum = pd.to_datetime(data.Datum)
        self.imported_data.Datum = pd.to_datetime(self.imported_data.Datum)
        self.imported_data.ix[data.index,data.columns]=data
        msg = "{} transaction imported".format(data.shape[0])
        self.main.status.showMessage(msg)

        from datacollect import save_database
        imported_data = self.imported_data.set_index('Hash',drop=False)
        imported_data.drop('Database',axis=1,inplace=True)
        imported_data.Kategorie = pd.Categorical(imported_data.Kategorie,categories=self.budget.Kategorie.tolist())
        self.db = imported_data.combine_first(self.db)
        self.db.sort('Datum',inplace=True)
        save_database(self.db)


    def dataImport(self):

        self.main = self.parent().parent().parent()

        start = self.period.dateFrom.selectedDate().toPyDate()
        stop = self.period.dateTo.selectedDate().toPyDate()


        callback=lambda x:self.main.progress.setValue(int(x))

        self.loader = ImportData(self.main,self.sources,start,stop,callback,self)
        self.loader.finished.connect(self.dataImported)

        self.loader.start()

    def dataImported(self):

        start = self.loader.start_date
        stop = self.loader.stop_date
        data = self.loader.data

        if len(data)<1:
            self.main.status.showMessage('Nothing to import in the selected period!',2000)
            return

        from datacollect import load_budget
        budget = load_budget(start=start,stop=stop)
        self.budget = budget

        import numpy as np
        data.drop('Unterkategorie',axis=1,inplace=True)
        data.Kategorie = pd.Categorical([np.NaN]*data.shape[0],categories=budget.Kategorie)

        hashes = self.create_hashes(data)
        db = load_database(budget.Kategorie.tolist())
        db.set_index('Hash',inplace=True,drop=False)

        self.db = db

        in_db = hashes.isin(db.index)
        data['Database']=in_db
        data['Deleted']=False
        data.set_index(hashes,inplace=True)

        joined=data.join(db,how='inner',lsuffix='_data')[['Kategorie','Deleted']]
        data.ix[joined.index,['Kategorie','Deleted']]=joined

        data=data[['Datum','Text','Lastschrift','Database','Deleted','Kategorie']]
        data.reset_index(inplace=True)

        self.imported_data = data

        # categorize
        import pickle, os
        if os.path.isfile(clf_file):
            with open(clf_file,'rb') as fp:
                clf = pickle.load(fp)

        classes = pd.Series(clf.classes_names,name='Kategorie')
        I = ~in_db
        if I.any():
            prediction = classes[clf.predict(data[I].Text)]
            data.loc[I,'Deleted'] = (prediction == 'Delete').values
            guessed = pd.Categorical(prediction,categories=classes)

            data.Kategorie = pd.Categorical(data.Kategorie,classes)
            data.loc[I,'Kategorie'] = guessed

        data.loc[data.Deleted,'Kategorie']=np.nan
        data.Kategorie = pd.Categorical(data.Kategorie,self.budget.Kategorie.tolist())

        self.main.status.clearMessage()
        self.main.progress.setValue(0)

        self.table = TransactionTable(data.loc[:,['Datum','Text','Lastschrift','Database','Deleted','Kategorie']],self)
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
        self.buttonReport = QtW.QPushButton("Create Report",self)
        self.buttonReport.clicked.connect(self.createReport)

        self.initUI()

    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        layout.addStretch(1)
        row = QtW.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.buttonReport)
        layout.addLayout(row)
        self.setLayout(layout)

    def createReport(self):
        import calendar

        self.main = self.parent().parent().parent()

        start = self.period.dateFrom.selectedDate().toPyDate()
        stop = self.period.dateTo.selectedDate().toPyDate()
        budget = load_budget(start,stop)

        db = load_database(budget.Kategorie.tolist())
        db.drop(db.Deleted,axis=0,inplace=True)
        db.drop('Deleted',axis=1,inplace=True)

        db = db[(db.Datum>=start)&(db.Datum<=stop)]

        print db.groupby([lambda i: db.ix[i,'Kategorie'],lambda i: calendar.month_name[db.ix[i,'Datum'].month]]).sum()




class FinanceMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowIcon(QIcon(r'res/icon.png'))

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

class ImportData(QThread):

    def __init__(self, main, sources, start, stop, callback, parent=None):

        QThread.__init__(self,parent=parent)

        self.start_date,self.stop_date = start, stop
        self.main = main
        self.callback = callback
        self.sources = sources

    def run(self):
        from datacollect import load_Expenses_from_Dropbox, load_MasterCardData, load_PostFinanceData, expand_EFinance

        start, stop = self.start_date,self.stop_date
        main = self.main
        callback = self.callback

        data = []

        if self.sources.expenses.isChecked():
            try:
                data.append(load_Expenses_from_Dropbox(start,stop))
            except:
                pass

        if self.sources.postfinance.isChecked():
            try:
                main.status.showMessage("load data from PostFinance extracts...")
                data.append(load_PostFinanceData(start,stop,callback=callback))
            except:
                pass

        if self.sources.mastercard.isChecked():
            callback(0)
            try:
                main.status.showMessage("load data from MasterCard extracts...")
                data.append(load_MasterCardData(start,stop,callback=callback))
            except:
                pass

        # Merge data
        data = pd.concat(data,axis=0)
        data = expand_EFinance(data)
        data.set_index('Datum',drop=False,inplace=True)
        data.sort(inplace=True)
        data.reset_index(inplace=True,drop=True)

        self.data = data