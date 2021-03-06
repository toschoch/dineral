#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtGui import QIcon

from ..plots import reporter

from .qtfinance import FinanceDataImport, FinanceReport
from .qtfinanceedit import FinanceTransactions
from .qtfinanceview import FinanceView
from .qtsettings import Settings
from .qtinfo import Info, AccountSelector

from ..internaldata import Budget, Database, Classifier, Report, Data
from ..internaldata.property import accounts, Property
from ..dataplugins import plugins

from builtins import str

class FinanceMain(QMainWindow):
    def __init__(self, **kwargs):
        QMainWindow.__init__(self)

        self.version = kwargs.pop('version','develop')

        # run account selector
        available = accounts()
        acc = AccountSelector(available.keys(), parent=self)
        acc.exec_()
        selected = acc.selectAccount.currentText()

        self.loadAccount(available, selected)

        self.setWindowIcon(QIcon(r'res/dineral.png'))

        self.main = FinanceMainWidget(parent=self, plugins=self.plugins, **kwargs)

        self.setCentralWidget(self.main)

        self.initMenu()

        self.classifier_clf = self.classifier.load()

    def loadAccount(self, available, selected):

        Property._account = selected
        plugin_names = [p.__name__ for p in plugins]

        self.plugins = [p() for pn, p in zip(plugin_names, plugins) if pn in available[selected]]
        self.setWindowTitle("Dineral ({}) - '{}'".format(self.version,self.plugins[0].account()))

        self.budget = Budget()
        self.database = Database()

        self.classifier = Classifier()
        self.report = Report()

        self.report_data_dir = Data()

    def initMenu(self):
        menubar = self.menuBar()
        entryMenu = menubar.addMenu('&Menu')
        actionSettings = QtW.QAction('&Settings', self)
        actionSettings.triggered.connect(self.settings)
        actionQuit = QtW.QAction('&Quit', self)
        actionQuit.triggered.connect(self.close)
        entryMenu.addAction(actionSettings)
        entryMenu.addSeparator()
        entryMenu.addAction(actionQuit)

        entryDb = menubar.addMenu('&Database')
        actionLoadAll = QtW.QAction('&Load all data...', self)
        actionLoadAll.triggered.connect(self.database_load_all)
        actionInfoDB = QtW.QAction('&Info', self)
        actionInfoDB.triggered.connect(self.database_info)
        entryDb.addAction(actionLoadAll)
        entryDb.addSeparator()
        entryDb.addAction(actionInfoDB)

        entryClf = menubar.addMenu('&Classifier')
        actionInfoClf = QtW.QAction('&Info', self)
        actionInfoClf.triggered.connect(self.classifier_info)
        entryClf.addAction(actionInfoClf)

    def settings(self):
        settings = Settings(sources=self.plugins, output=[self.report, self.report_data_dir],
                            internal=[self.budget, self.database, self.classifier])
        settings.exec_()

    def classifier_info(self):
        info = [['Type', str(self.classifier_clf._final_estimator)],
                ['File:', self.classifier.properties],
                ['Classes:', u", ".join(map(str, self.classifier_clf.classes_names))],
                ['Trained:',
                 str(self.classifier.date_training()) + ' on {} samples'.format(self.classifier.training_samples())],
                ['Score (precision, recall, f1):',
                 str(self.classifier.test_score()) + ' on {} samples'.format(self.classifier.test_samples())]]
        clf_info = Info(info=info, header='Classifier')
        clf_info.exec_()

    def database_info(self):
        db = self.database.data
        info = [['File:', self.database.properties],
                ['Size:', "{} Bytes".format(self.database.get_size())],
                ['Entries:', "{}".format(len(db))],
                ['Period:', "{} to {}".format(db.Datum.min(), db.Datum.max())]]
        db_info = Info(info=info, header='Database')
        db_info.exec_()

    def database_load_all(self):
        db = self.database.data
        db['Database'] = True
        db = db[self.main.transactions.table.columns]

        main = self.main
        main.transactions.setData(db)

        main.content.setCurrentWidget(main.transactions)


class FinanceMainWidget(QWidget):
    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent)

        self.control = QtW.QTabWidget(self)
        self.dataimport = FinanceDataImport(parent=self, **kwargs)
        self.report = FinanceReport(self)
        self.content = QtW.QTabWidget(self)
        self.transactions = FinanceTransactions(self)
        self.graphview = FinanceView(self)

        self.initUI()

    def initUI(self):
        self.control.addTab(self.dataimport, "Import")
        self.control.addTab(self.report, "Report")

        self.content.addTab(self.transactions, 'Transactions')
        self.content.addTab(self.graphview, 'View')
        self.content.currentChanged.connect(self.contentChanged)

        layout = QtW.QHBoxLayout()
        layout.addWidget(self.control, 0)
        layout.addWidget(self.content, 1)
        self.setLayout(layout)

    def contentChanged(self, i):
        if self.content.tabText(i) == 'View':
            from ..plots import reporter
            from ..plots.style import set_style

            set_style('gui')

            self.control.setCurrentWidget(self.report)

            window = self.window()

            # reload database
            window.database.reload_data()

            reporter.statistics(window)

            self.graphview.comboGraph.clear()
            self.graphview.comboGraph.addItems(reporter.plots)
            self.graphview.PlotSelected()

            self.graphview.comboGraph.setFocus()
