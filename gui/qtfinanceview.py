#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceview.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget

from plots import reporter
import seaborn
seaborn.set_context("notebook", rc={"lines.linewidth": 3}, font_scale=1.3)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

class FinanceView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.graph = FinanceGraph(self)
        self.lblHeader = QtW.QLabel("Show: ",self)
        self.comboGraph = QtW.QComboBox(self)
        self.comboGraph.addItem('Total')
        self.comboGraph.currentIndexChanged.connect(self.PlotSelected)

        self.toolbar = NavigationToolbar2QT(self.graph,self)

        self.reporter = reporter

        self.initUI()

    def initUI(self):

        vlayout = QtW.QVBoxLayout(self)

        hl = QtW.QHBoxLayout()
        hl.addWidget(self.lblHeader,0)
        hl.addWidget(self.comboGraph,1)

        vlayout.addLayout(hl,0)

        vlayout.addWidget(self.graph,1)
        vlayout.addWidget(self.toolbar,0)

        self.setContentsMargins(0,0,0,0)

    def PlotSelected(self, i=None):

        if not i:
            i = self.comboGraph.currentIndex()

        if i<0:
            return

        category = self.comboGraph.itemText(i)

        window = self.window()
        self.graph.clear()

        self.reporter.plot(window,category,self.graph.axes)

        self.graph.draw()

class FinanceGraph(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.gca()

        FigureCanvasQTAgg.__init__(self,self.figure)
        self.setParent(parent)

        self.setSizePolicy(QtW.QSizePolicy.Expanding,QtW.QSizePolicy.Expanding)
        self.updateGeometry()

    def clear(self):
        self.figure.clear()
        self.axes = self.figure.gca()