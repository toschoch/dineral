#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceedit.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

import logging
log = logging.getLogger(__name__)

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget

from qttransactiontable import TransactionTable

class FinanceTransactions(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.table = TransactionTable(parent=self)

        self.btnSave = QtW.QPushButton("Save",self)
        self.btnSave.setEnabled(False)
        self.btnSave.clicked.connect(self.save)
        self.btnCancel = QtW.QPushButton("Cancel",self)
        self.btnCancel.setEnabled(False)
        self.btnCancel.clicked.connect(self.clear)

        # self.lblHeader = QtW.QLabel("Period: ",self)
        # self.lblHeader.setFixedHeight(22)
        # self.lblPeriod = QtW.QLabel("1. April 2015 - 30. November 2015",self)

        # self.lblStatus = QtW.QLabel(self)

        self.initUI()

    def save(self):

        data = self.table.dataModel.df
        log.info("save {} entries to database...".format(len(data)))

        main = self.window()

        db = main.database.data
        db = data.drop('Database',axis=1).combine_first(db)
        db.sort('Datum',inplace=True)

        db.save_data(main.database_data)

        self.clear()

    def clear(self):
        self.btnSave.setEnabled(False)
        self.btnCancel.setEnabled(False)
        self.table.setDataFrame(None)

    def setData(self, data=None):
        enabled = (data is not None)
        self.btnSave.setEnabled(enabled)
        self.btnCancel.setEnabled(enabled)
        self.table.setDataFrame(data)

    def initUI(self):

        vlayout = QtW.QVBoxLayout(self)

        # hl = QtW.QHBoxLayout()
        # hl.addWidget(self.lblHeader,0)
        # hl.addWidget(self.lblPeriod,0)
        # hl.addStretch(1)
        #
        # vlayout.addLayout(hl,0)
        vlayout.addWidget(self.table,1)

        hl = QtW.QHBoxLayout()
        # hl.addWidget(self.lblStatus,0)
        hl.addStretch(1)
        hl.addWidget(self.btnSave,0)
        hl.addWidget(self.btnCancel,0)

        vlayout.addLayout(hl)

        self.setLayout(vlayout)

        self.setContentsMargins(0,0,0,0)