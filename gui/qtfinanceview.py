#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceview.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget
import seaborn
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

# set some settings for the style
mpl.rcParams['xtick.labelsize']='large'
mpl.rcParams['ytick.labelsize']='large'
class FinanceView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.graph = FinanceGraph(self)

        self.lblHeader = QtW.QLabel("Show: ",self)
        self.comboGraph = QtW.QComboBox(self)
        self.comboGraph.addItem('Total')
        # self.lblPeriod = QtW.QLabel("1. April 2015 - 30. November 2015",self)

        self.toolbar = NavigationToolbar2QT(self.graph,self)

        # self.lblStatus = QtW.QLabel(self)

        self.initUI()

    def initUI(self):

        vlayout = QtW.QVBoxLayout(self)

        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblHeader,0)
        hl.addWidget(self.comboGraph,1)

        vlayout.addLayout(hl,0)

        vlayout.addWidget(self.graph,1)
        vlayout.addWidget(self.toolbar,0)

        # hl.addWidget(self.lblPeriod,0)
        # hl.addStretch(1)
        #

        self.setContentsMargins(0,0,0,0)

class FinanceGraph(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.gca()

        FigureCanvasQTAgg.__init__(self,self.figure)
        self.setParent(parent)

        self.setSizePolicy(QtW.QSizePolicy.Expanding,QtW.QSizePolicy.Expanding)
        self.updateGeometry()