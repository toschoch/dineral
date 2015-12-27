#!/usr/bin/env python
# encoding: utf-8
"""
gui.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

import logging
log = logging.getLogger(__name__)

from PyQt5 import QtWidgets as QtW
from PyQt5.QtCore import QDate

from qtutils import QCheckBoxGroup, FinanceSelector
from qtimport import DataImport

import pandas as pd

clf_file = 'data/classifier.pickle'

class FinanceDataImport(FinanceSelector):

    def __init__(self, plugins, parent=None):
        FinanceSelector.__init__(self,parent)

        self.sources = QCheckBoxGroup([d.name() for d in plugins],'Import from:',self)
        self.btnImport = QtW.QPushButton("Import",self)
        self.importer = DataImport(plugins,parent=self)

        self.initUI()
        self.setStartDate()

        self.importer.success.connect(self.showData)
        self.btnImport.clicked.connect(self.importData)


    def initUI(self):

        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        # layout.addWidget(self.info)
        layout.addWidget(self.sources)
        layout.addStretch(1)

        row = QtW.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btnImport)
        layout.addLayout(row)

    def setStartDate(self):

        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),today.month()-1,1))
        self.period.dateTo.setSelectedDate(QDate(today.year(),today.month()-1,QDate(today.year(),today.month()-1,1).daysInMonth()))

    def importData(self):

        start = self.period.dateFrom.selectedDate().toPyDate()
        stop = self.period.dateTo.selectedDate().toPyDate()

        self.selectedPeriod = (start,stop)

        for check,plugin in zip(self.sources.checkboxes,self.importer.plugins):
            plugin.LOAD = check.isChecked()

        self.importer.start(start,stop)

    def showData(self, data):

        window = self.window()

        db = window.database.data
        db.set_index('Hash',inplace=True,drop=False)

        import numpy as np
        data.Kategorie = pd.Categorical([np.NaN]*data.shape[0],categories=db.Kategorie.cat.categories)

        hashes = self.create_hashes(data)

        log.info("lookup imported data in database...")
        in_db = hashes.isin(db.index)
        data['Database']=in_db
        data['Deleted']=False
        data.set_index(hashes,inplace=True)
        log.info("found {} of {} entries in database...".format(in_db.sum(),len(data)))

        joined=data.join(db,how='inner',lsuffix='_data')[['Kategorie','Deleted']]
        joined.Kategorie = pd.Categorical(joined.Kategorie,data.Kategorie.cat.categories)
        data.ix[joined.index,['Kategorie','Deleted']]=joined

        data=pd.DataFrame(data[['Datum','Text','Lastschrift','Database','Deleted','Kategorie']])
        data.reset_index(inplace=True)

        clf = window.classifier_clf

        classes = pd.Series(clf.classes_names,name='Kategorie')
        I = ~in_db
        if I.any():
            log.info("classify imported data...")
            prediction = classes[clf.predict(data[I].Text)]
            data.loc[I,'Deleted'] = (prediction == 'Delete').values
            prediction[prediction == 'Delete'] = np.NaN
            guessed = pd.Categorical(prediction,categories=data.Kategorie.cat.categories)
            data.loc[I,'Kategorie'] = guessed
            log.info("categorized {} new entries...".format(len(guessed)))

        data.ix[data.Deleted,'Kategorie']=np.nan
        data.Kategorie = pd.Categorical(data.Kategorie,db.Kategorie.cat.categories)

        main = window.main
        main.transactions.setData(data)

        main.transactions.table.dataTable.setFocus()


    @staticmethod
    def create_hashes(data):

        import hashlib
        from unidecode import unidecode

        def hash(row):
            h = hashlib.md5(unidecode(row['Datum'].strftime('%d-%m-%Y').decode('utf-8'))+' '+unidecode(row['Text'])+' '+'CHF {0:.0f}'.format(row['Lastschrift'])).hexdigest()
            return pd.Series({'Hash':h})

        return data.apply(hash,axis=1).Hash


class FinanceReport(FinanceSelector):
    def __init__(self, parent=None):

        FinanceSelector.__init__(self,parent)

        self.btnReport = QtW.QPushButton("Create Report",self)
        self.btnReport.clicked.connect(self.createReport)

        self.initUI()
        self.setStartDate()


    def initUI(self):
        layout = QtW.QVBoxLayout(self)
        layout.addWidget(self.period)
        # layout.addWidget(self.info)
        layout.addStretch(1)
        row = QtW.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.btnReport)
        layout.addLayout(row)
        self.setLayout(layout)

    def setStartDate(self):
        today = QDate.currentDate()
        self.period.dateFrom.setSelectedDate(QDate(today.year(),1,1))

    def createReport(self):

        window = self.window()
        main = window.main
        main.showReport()
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