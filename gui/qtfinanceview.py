#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceview.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget

import pandas as pd
import datetime
import seaborn
seaborn.set_context("notebook", rc={"lines.linewidth": 3}, font_scale=1.3)
import matplotlib as mpl
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

    def PlotSelected(self, i=None):
        from plots.statistics import calculate_monthly
        from plots.defaults import monthly_settings
        from plots.categories import plot_income, plot_expense

        colors = iter(seaborn.color_palette())

        window = self.window()
        db = window.database.data
        budget = window.budget.data

        data = db[db.Datum>=datetime.date(window.selected_year,1,1)]

        if not i:
            i = self.comboGraph.currentIndex()

        if i<0:
            return

        category = self.comboGraph.itemText(i)

        monthly_sum = calculate_monthly(data)

        self.graph.axes.cla()

        budget = budget.set_index('Kategorie')
        if budget.ix[category,'Jahresbudget'] > 0:
            plot_income(self.graph.axes, monthly_sum, budget, category)
        else:
            plot_expense(self.graph.axes, monthly_sum, budget, category)

        monthly_settings(self.graph.axes)

        self.graph.draw()

        # print monthly_sum




class FinanceGraph(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.gca()

        FigureCanvasQTAgg.__init__(self,self.figure)
        self.setParent(parent)

        self.setSizePolicy(QtW.QSizePolicy.Expanding,QtW.QSizePolicy.Expanding)
        self.updateGeometry()