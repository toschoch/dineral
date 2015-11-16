#!/usr/bin/env python
# encoding: utf-8
"""
transactiontable.py

Created by Tobias Schoch on 16.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QMainWindow, QSizePolicy
from PyQt5.QtCore import Qt, QModelIndex, QDate, QEvent
from PyQt5.QtGui import QIcon, QKeyEvent

import pandas as pd
from qtpandas import DataFrameWidget, DataFrameModel


class TransactionTableView(QtW.QTableView):

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space or event.key() == Qt.Key_Return:
            if self.state() == self.EditingState:
                event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
                QtW.QTableView.keyPressEvent(self,event)
            else:
                self.edit(self.currentIndex())
        elif event.key() == Qt.Key_Delete or event.key()==Qt.Key_D:
            index = self.currentIndex()
            model = self.model()
            c = model.df.columns.tolist().index('Deleted')
            index = model.index(index.row(),c)
            value = model.data(index,Qt.DisplayRole)
            model.setData(index,not eval(value.value()),Qt.EditRole)
            self.update(index)

        else:
            QtW.QTableView.keyPressEvent(self,event)

class TransactionTable(DataFrameWidget):

    def __init__(self, data, parent=None):
        super(DataFrameWidget, self).__init__(parent)
        self.dataModel = DataFrameModel(self)
        self.dataTable = TransactionTableView(self)
        self.dataTable.setModel(self.dataModel)

        self.dataTable.setSelectionBehavior(QtW.QTableView.SelectRows)
        self.dataTable.setEditTriggers(QtW.QTableView.SelectedClicked)
        self.dataTable.setWordWrap(True)

        # Set DataFrame
        self.setDataFrame(data)
        self.initUI()

        self.i_cat = data.columns.tolist().index('Kategorie')
        self.dataTable.setCurrentIndex(self.dataModel.index(0,self.i_cat))
        self.dataTable.setColumnWidth(self.i_cat,200)
        h = self.getMaxColumnHeight()
        for i in range(self.dataModel.rowCount()):
            self.dataTable.setRowHeight(i,h)
        self.setFixedWidth(self.getWidth())
        self.setMinimumHeight(400)

        self.setWindowTitle('Transactions')
