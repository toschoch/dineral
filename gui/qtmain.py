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

from qtfinance import FinanceDataImport, FinanceReport
from qtfinanceedit import FinanceTransactions, FinanceView
from qtsettings import Settings

class FinanceMain(QMainWindow):

    def __init__(self, plugins, **kwargs):
        QMainWindow.__init__(self)

        self.plugins = plugins

        self.setWindowIcon(QIcon(r'res/icon.png'))

        self.main = FinanceMainWidget(parent=self, plugins=plugins, **kwargs)

        self.setCentralWidget(self.main)

        self.initMenu()

    def initMenu(self):

        menubar = self.menuBar()
        entryMenu = menubar.addMenu('&Menü')
        actionSettings = QtW.QAction('&Settings',self)
        actionSettings.triggered.connect(self.settings)
        actionQuit = QtW.QAction('&Quit',self)
        actionQuit.triggered.connect(self.close)
        entryMenu.addAction(actionSettings)
        entryMenu.addSeparator()
        entryMenu.addAction(actionQuit)

        entryDb = menubar.addMenu('&Database')
        actionLoadAll = QtW.QAction('&Load all data...',self)
        actionInfoDB = QtW.QAction('&Info',self)
        entryDb.addAction(actionLoadAll)
        entryDb.addSeparator()
        entryDb.addAction(actionInfoDB)

        entryClf = menubar.addMenu('&Classifier')
        actionInfoClf = QtW.QAction('&Info',self)
        entryClf.addAction(actionInfoClf)

    def settings(self):

        settings = Settings(self.plugins,self.main)
        settings.exec_()



class FinanceMainWidget(QWidget):

    def __init__(self, parent=None, **kwargs):

        QWidget.__init__(self,parent)

        self.tab = QtW.QTabWidget(self)
        self.dataimport = FinanceDataImport(parent=self,**kwargs)
        self.report = FinanceReport(self)
        self.content = QtW.QStackedWidget(self)
        self.transactions = FinanceTransactions(self)
        self.graphview = FinanceView(self)

        self.initUI()

    def initUI(self):

        self.tab.addTab(self.dataimport, "Import")
        self.tab.addTab(self.report,"Report")

        self.content.addWidget(self.transactions)
        self.content.addWidget(self.graphview)
        self.content.setCurrentWidget(self.graphview)
        # self.content.hide()

        adj_layout = QtW.QHBoxLayout()
        adj_layout.addWidget(self.tab)
        adj_layout.setContentsMargins(9,9,9,9)

        layout = QtW.QHBoxLayout()
        layout.addLayout(adj_layout,0)
        layout.addWidget(self.content,1)
        self.setLayout(layout)