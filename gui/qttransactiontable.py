#!/usr/bin/env python
# encoding: utf-8
"""
qttransactiontable.py

Created by Tobias Schoch on 16.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QMainWindow, QSizePolicy, QStyledItemDelegate
from PyQt5.QtCore import Qt, QModelIndex, QDate, QEvent
from PyQt5.QtGui import QIcon, QKeyEvent, QBrush, QColor

from seaborn.palettes import color_palette
import pandas as pd

from qtpandas import DataFrameWidget, DataFrameModel, ComboBoxDelegate

class TransactionTableModel(DataFrameModel):

    def __init__(self, data, parent):

        DataFrameModel.__init__(self,parent)

        self.setDataFrame(data)

        self.deleted_color_back = (207,207,196,100)
        self.deleted_color_text = (207,207,196)

    def setDataFrame(self, data):

        self.i_deleted = data.columns.tolist().index('Deleted')
        self.i_categorie = data.columns.tolist().index('Kategorie')
        if data.empty:
            self.categories = []
            self.colors = color_palette('hls',n_colors=1)
            self.colors = [map(lambda x: int(255*x),c)+[160] for c in self.colors]
        else:
            self.categories = data['Kategorie'].cat.categories.tolist()
            self.colors = color_palette('hls',n_colors=len(self.categories))
            self.colors = [map(lambda x: int(255*x),c)+[160] for c in self.colors]

        DataFrameModel.setDataFrame(self,data)


    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundColorRole:
            if not self.df.ix[index.row(),'Deleted']:
                cat = self.df.ix[index.row(),'Kategorie']
                try:
                    color = self.colors[self.categories.index(cat)]
                    return QColor(*color)
                except ValueError:
                    return DataFrameModel.data(self,index,role)

            else:
                return QColor(*self.deleted_color_back)
        elif role == Qt.TextColorRole:
            if hasattr(self,'categories') and self.df.ix[index.row(),'Deleted']:
                return QColor(*self.deleted_color_text)
            else:
                return DataFrameModel.data(self,index,role)
        else:
            return DataFrameModel.data(self,index,role)



class TransactionTableView(QtW.QTableView):

    def __init__(self,parent):
        QtW.QTableView.__init__(self,parent)
        self.n_pressed = 0
        self.last_key = None

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Space:
            if self.state() == self.EditingState:
                event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
                QtW.QTableView.keyPressEvent(self,event)
            else:
                self.edit(self.currentIndex())
        elif event.key() == Qt.Key_Return:
            event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
            QtW.QTableView.keyPressEvent(self,event)
        elif event.key() == Qt.Key_Delete:
            index = self.currentIndex()
            model = self.model()
            c = model.i_deleted
            index = model.index(index.row(),c)
            value = model.data(index,Qt.DisplayRole)
            model.setData(index,not eval(value.value()),Qt.EditRole)
            for i in range(model.df.shape[1]):
                self.update(model.index(index.row(),i))
        elif event.text()<>"":
            t = event.text()
            index = self.currentIndex()
            model = self.model()
            categories = pd.Series(model.categories)
            cat = categories[categories.str.lower().str.startswith(t)]
            if len(cat)>0:
                if t == self.last_key:
                    self.n_pressed+=1
                else:
                    self.n_pressed = 0
                if self.n_pressed>=len(cat):
                    self.n_pressed = 0
                cat = cat.iloc[self.n_pressed]
                c = model.df.columns.tolist().index('Kategorie')
                index = model.index(index.row(),c)
                model.setData(index,cat,Qt.EditRole)
                for i in range(model.df.shape[1]):
                    self.update(model.index(index.row(),i))
                self.last_key = t
        else:
            QtW.QTableView.keyPressEvent(self,event)

class TransactionTable(DataFrameWidget):

    def __init__(self, data=pd.DataFrame(columns=['Datum','Text','Lastschrift','Database','Deleted','Kategorie']), parent=None):

        QWidget.__init__(self,parent=parent)
        self.parent_ = parent
        self.dataModel = TransactionTableModel(data,self)
        self.dataTable = TransactionTableView(self)
        self.dataTable.setModel(self.dataModel)
        self.dataTable.setItemDelegate(TransactionItemDelegate(self))
        self.dataTable.setStyleSheet("selection-background-color: transparent; selection-color:black")

        self.dataTable.setSelectionBehavior(QtW.QTableView.SelectRows)
        self.dataTable.setEditTriggers(QtW.QTableView.SelectedClicked)
        self.dataTable.setWordWrap(True)

        self.buttonSave = QtW.QPushButton("Save",self)
        self.buttonCancel = QtW.QPushButton("Cancel",self)

        self.buttonCancel.clicked.connect(self.close)
        self.buttonSave.clicked.connect(self.save)


        # Set DataFrame
        self.initUI()

        # Set DataFrame
        self.setDataFrame(data)


    def save(self):
        self.parent_.save_imported(self.dataModel.df)
        self.close()

    def initUI(self):
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QtW.QVBoxLayout()
        layout.addWidget(self.dataTable,1)
        row = QtW.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.buttonSave)
        row.addWidget(self.buttonCancel)
        layout.addLayout(row)
        self.setLayout(layout)

    def setDataFrame(self, data):
        self.dataModel.setDataFrame(data)
        for i,dt in enumerate(data.dtypes):
            try:
                self.dataTable.setItemDelegateForColumn(i,TransactionComboBoxItemDelegate(self,self.dataModel.categories+['nan']))
            except:
                if data.ix[:,i].dtype==bool:
                    self.dataTable.setItemDelegateForColumn(i,TransactionComboBoxItemDelegate(self,['True','False']))
        self.dataModel.signalUpdate()
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()

        self.i_cat = self.dataModel.i_categorie
        self.dataTable.setCurrentIndex(self.dataModel.index(0,self.i_cat))
        self.dataTable.setColumnWidth(self.i_cat,200)
        h = self.getMaxColumnHeight()
        for i in range(self.dataModel.rowCount()):
            self.dataTable.setRowHeight(i,h)
        self.setFixedWidth(self.getWidth())
        self.setMinimumHeight(400)

class TransactionItemDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):

        bg_color = index.data(Qt.BackgroundColorRole)
        painter.fillRect(option.rect, bg_color)
        QStyledItemDelegate.paint(self,painter,option,index)

class TransactionComboBoxItemDelegate(TransactionItemDelegate,ComboBoxDelegate):
    pass
