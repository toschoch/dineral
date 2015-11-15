#!/usr/bin/env python
# encoding: utf-8
"""
qtpandas.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex
from PyQt5.QtWidgets import QVBoxLayout, QTableView, QWidget, QSizePolicy, QItemDelegate, QApplication, QStyleOptionComboBox, QStyle, QComboBox
from pandas import DataFrame, Categorical
from numpy import NaN


class DataFrameModel(QAbstractTableModel):
    ''' data model for a DataFrame class '''

    def __init__(self):
        super(DataFrameModel, self).__init__()
        self.df = DataFrame()

    def setDataFrame(self, dataFrame):
        self.df = dataFrame

    def signalUpdate(self):
        ''' tell viewers to update their data (this is full update, not
        efficient)'''
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError,):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self.df.index.tolist()[section]
            except (IndexError,):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()

        if not index.isValid():
            return QVariant()

        value = self.df.ix[index.row(), index.column()]
        try:
            text = unicode(value)
        except UnicodeDecodeError:
            text = unicode(value.decode('utf-8'))
        return QVariant(text)

    def flags(self, index):
        flags = super(DataFrameModel, self).flags(index)
        flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role):
        row = self.df.index[index.row()]
        col = self.df.columns[index.column()]
        self.df.set_value(row, col, value)
        return True

    def rowCount(self, index=QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self.df.shape[1]


class DataFrameWidget(QWidget):
    ''' a simple widget for using DataFrames in a gui '''

    def __init__(self, dataFrame, parent=None):
        super(DataFrameWidget, self).__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.dataModel = DataFrameModel()
        self.dataTable = QTableView()
        self.dataTable.setModel(self.dataModel)
        self.dataTable.setSelectionBehavior(QTableView.SelectRows)
        self.dataTable.setEditTriggers(QTableView.AllEditTriggers)
        self.dataTable.setWordWrap(True)

        for i,dt in enumerate(dataFrame.dtypes):
            try:
                self.dataTable.setItemDelegateForColumn(i,ComboBoxDelegate(self,dataFrame.ix[:,i].cat.categories.tolist()+['nan']))
            except:
                pass


        layout = QVBoxLayout()
        layout.addWidget(self.dataTable)
        self.setLayout(layout)
        # Set DataFrame
        self.setDataFrame(dataFrame)

    def getMaxColumnHeight(self):
        return max([self.dataTable.rowHeight(i) for i in range(self.dataModel.rowCount())])


    def getWidth(self):

        margs = self.layout().getContentsMargins()
        w = margs[0]+margs[2]+20
        for i in range(self.dataModel.columnCount()):
            w+=self.dataTable.columnWidth(i)
        return w

    def setDataFrame(self, dataFrame):
        self.dataModel.setDataFrame(dataFrame)
        self.dataModel.signalUpdate()
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()

class ComboBoxDelegate(QItemDelegate):
    def __init__(self, owner, itemslist):
        QItemDelegate.__init__(self, owner)
        self.itemslist = itemslist

    def paint(self, painter, option, index):
        # Get Item Data
        value = index.data(Qt.EditRole)
        # fill style options with item data
        style = QApplication.style()
        opt = QStyleOptionComboBox()
        opt.text = unicode(value)
        opt.rect = option.rect

        # draw item data as ComboBox
        style.drawComplexControl(QStyle.CC_ComboBox, opt, painter)
        QItemDelegate.paint(self,painter,option,index)

    def createEditor(self, parent, option, index):
        value = index.data(Qt.DisplayRole)
        editor = QComboBox(parent)
        editor.addItems(self.itemslist)
        editor.setCurrentText(value)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText().encode('utf-8')
        if value=='nan':
            value = NaN
        model.setData(index, value, Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)