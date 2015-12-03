#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceedit.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class FinanceTransactions(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.table = QtW.QTableView(self)

        self.btnSave = QtW.QPushButton("Save",self)
        self.btnCancel = QtW.QPushButton("Cancel",self)

        self.lblHeader = QtW.QLabel("Period: ",self)
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

        panel = QtW.QFrame(self)
        panel.setFrameShape(panel.Box)
        panel.setFrameShadow(panel.Sunken)
        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblStatus,0)
        hl.addStretch(1)
        hl.addWidget(self.btnSave,0)
        hl.addWidget(self.btnCancel,0)
        panel.setLayout(hl)

        vlayout.addWidget(panel)

        self.setContentsMargins(0,0,0,0)

class FinanceGraph(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.gca()

        FigureCanvasQTAgg.__init__(self,self.figure)
        self.setParent(parent)

        self.setSizePolicy(QtW.QSizePolicy.Expanding,QtW.QSizePolicy.Expanding)
        self.updateGeometry()

class FinanceView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.graph = FinanceGraph(self)

        self.lblHeader = QtW.QLabel("Period: ",self)
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
        vlayout.addWidget(self.graph,1)

        panel = QtW.QFrame(self)
        panel.setFrameShape(panel.Panel)
        panel.setFrameShadow(panel.Raised)
        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblStatus,0)
        hl.addStretch(1)
        panel.setLayout(hl)

        vlayout.addWidget(panel)

        self.setContentsMargins(0,0,0,0)
