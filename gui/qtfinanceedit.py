#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceedit.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget

from qttransactiontable import TransactionTable

class FinanceTransactions(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # self.table = QtW.QTableView(self)
        self.table = TransactionTable(parent=self)

        self.btnSave = QtW.QPushButton("Save",self)
        self.btnCancel = QtW.QPushButton("Cancel",self)

        self.lblHeader = QtW.QLabel("Period: ",self)
        self.lblHeader.setFixedHeight(22)
        self.lblPeriod = QtW.QLabel("1. April 2015 - 30. November 2015",self)

        self.lblStatus = QtW.QLabel(self)

        self.initUI()

    def initUI(self):

        vlayout = QtW.QVBoxLayout(self)

        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblHeader,0)
        hl.addWidget(self.lblPeriod,0)
        hl.addStretch(1)

        vlayout.addLayout(hl,0)
        vlayout.addWidget(self.table,1)

        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblStatus,0)
        hl.addStretch(1)
        hl.addWidget(self.btnSave,0)
        hl.addWidget(self.btnCancel,0)

        vlayout.addLayout(hl)

        self.setContentsMargins(0,0,0,0)