#!/usr/bin/env python
# encoding: utf-8
"""
qtpandas.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""
from PySide.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide.QtGui import QVBoxLayout, QTableView, QWidget, QSizePolicy, QItemDelegate, QApplication, \
    QStyleOptionComboBox, QStyle, QComboBox
from pandas import DataFrame, Categorical
from numpy import NaN


class DataFrameModel(QAbstractTableModel):
    ''' data model for a DataFrame class '''

    def __init__(self, parent):
        super(DataFrameModel, self).__init__(parent)
        self.df = DataFrame()

    def setDataFrame(self, dataFrame):
        self.layoutAboutToBeChanged.emit()
        self.df = dataFrame
        self.layoutChanged.emit()

    def signalUpdate(self):
        ''' tell viewers to update their data (this is full update, not
        efficient)'''
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return

        if orientation == Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError,):
                return
        elif orientation == Qt.Vertical:
            try:
                return self.df.index.tolist()[section]
            except (IndexError,):
                return

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return

        if not index.isValid():
            return

        text = self.df.ix[index.row(), index.column()]
        try:
            text = unicode(text)
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

        return text

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
        self.dataModel = DataFrameModel(self)
        self.dataTable = QTableView(self)
        self.dataTable.setModel(self.dataModel)
        self.dataTable.setSortingEnabled(True)

        self.initUI()

        # Set DataFrame
        self.setDataFrame(dataFrame)

    def initUI(self):
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QVBoxLayout()
        layout.addWidget(self.dataTable)
        self.setLayout(layout)

    def getMaxRowHeight(self):
        return max([self.dataTable.rowHeight(i) for i in range(self.dataModel.rowCount())] + [10])

    def getWidth(self):

        margs = self.layout().getContentsMargins()
        w = margs[0] + margs[2] + 20
        for i in range(self.dataModel.columnCount()):
            w += self.dataTable.columnWidth(i)
        return w

    def setDataFrame(self, dataFrame):
        self.dataModel.setDataFrame(dataFrame)
        for i, dt in enumerate(dataFrame.dtypes):
            try:
                self.dataTable.setItemDelegateForColumn(i, ComboBoxDelegate(self, dataFrame.ix[:,
                                                                                  i].cat.categories.tolist() + ['nan']))
            except:
                if dataFrame.ix[:, i].dtype == bool:
                    self.dataTable.setItemDelegateForColumn(i, ComboBoxDelegate(self, ['True', 'False']))
        self.dataModel.signalUpdate()
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()
        self.dataModel.sort(1)


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, owner, itemslist):
        QItemDelegate.__init__(self, owner)
        self.itemslist = itemslist

    def createEditor(self, parent, option, index):
        value = index.data(Qt.DisplayRole)
        editor = QComboBox(parent)
        editor.addItems(self.itemslist)
        editor.setCurrentIndex(self.itemslist.index(value))
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole)
        editor.setCurrentIndex(self.itemslist.index(value))

    def setModelData(self, editor, model, index):
        value = editor.currentText()#.encode('utf-8')
        if value == 'nan':
            value = NaN
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        model.setData(index, value, Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
