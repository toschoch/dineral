#!/usr/bin/env python
# encoding: utf-8
"""
qtfinanceview.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget

import datetime
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
        from plots.statistics import calculate_monthly, calculate_summary
        from plots.categories import plot
        from plots import additional_plots, additional_plots_names

        colors = iter(seaborn.color_palette())

        window = self.window()
        db = window.database.data
        budget = window.budget.data

        if not i:
            i = self.comboGraph.currentIndex()

        if i<0:
            return

        category = self.comboGraph.itemText(i)


        monthly_sum = calculate_monthly(db, date_from=window.budget.date_from)
        budget = calculate_summary(monthly_sum, budget, date_from=window.budget.date_from, date_to=db.Datum.max())

        if category in additional_plots_names:

            additional_plots[additional_plots_names.index(category)].plot(monthly_sum,budget,self.graph.axes)

        else:

            self.graph.axes.cla()

            plot(category,monthly_sum,budget,self.graph.axes)

            self.graph.draw()


class FinanceGraph(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure()
        self.axes = self.figure.gca()

        FigureCanvasQTAgg.__init__(self,self.figure)
        self.setParent(parent)

        self.setSizePolicy(QtW.QSizePolicy.Expanding,QtW.QSizePolicy.Expanding)
        self.updateGeometry()