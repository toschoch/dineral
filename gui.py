#!/usr/bin/env python
# encoding: utf-8
"""
gui.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout

import pandas as pd
from qtpandas import DataFrameWidget
from dataload import load_MasterCardExtract
from datacollect import load_budget


import pandas as pd

class FinanceApp(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self,parent)

        data = load_MasterCardExtract(r'/home/tobi/Finance/e-Rechnungen/Mastercard/2015/Oktober.pdf',300)
        budget = load_budget(pd.to_datetime('2015-01-01'))
        data.Kategorie = pd.Categorical(data.Kategorie,categories=budget.Kategorie.tolist())

        self.data = DataFrameWidget(dataFrame=data)

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout(self)
        layout.addWidget(self.data)
        self.setLayout(layout)


class FinanceMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MyFinance')
        self.setCentralWidget(FinanceApp(self))