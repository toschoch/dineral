#!/usr/bin/env python
# encoding: utf-8
"""
qttransactiontable.py

Created by Tobias Schoch on 16.11.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget, QSizePolicy, QStyledItemDelegate
from PyQt5.QtCore import Qt, QEvent, QVariant, QAbstractTableModel, QSortFilterProxyModel
from PyQt5.QtGui import QKeyEvent, QColor

from seaborn.palettes import color_palette
import pandas as pd

from qtpandas import DataFrameWidget, DataFrameModel, ComboBoxDelegate


class TransactionTableModel(DataFrameModel):
    def __init__(self, data, parent):

        DataFrameModel.__init__(self, parent)

        self.setDataFrame(data)

        self.deleted_color_back = (207, 207, 196, 100)
        self.deleted_color_text = (207, 207, 196)

    def setDataFrame(self, data):

        columns = data.columns.tolist()
        self.i_datum = columns.index('Datum')
        self.i_deleted = columns.index('Deleted')
        self.i_categorie = columns.index('Kategorie')
        self.i_database = columns.index('Database')
        convert_color = lambda lst: [map(lambda x: int(255 * x), c) + [160] for c in lst]
        if data.empty:
            self.categories = []
            self.colors = color_palette('Set2', n_colors=1)
            self.colors = convert_color(self.colors)
        else:
            self.categories = data['Kategorie'].cat.categories.tolist()
            self.categories.sort()
            self.colors = color_palette('Set2', n_colors=len(self.categories))
            self.colors = convert_color(self.colors)

        DataFrameModel.setDataFrame(self, data)

    def flags(self, index):
        if index.column() == self.i_database:
            return QAbstractTableModel.flags(self, index)
        else:
            return DataFrameModel.flags(self, index)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundColorRole:
            if not self.df.ix[index.row(), 'Deleted']:
                cat = self.df.ix[index.row(), 'Kategorie']
                try:
                    color = self.colors[self.categories.index(cat)]
                    return QColor(*color)
                except ValueError:
                    return DataFrameModel.data(self, index, role)

            else:
                return QColor(*self.deleted_color_back)
        elif role == Qt.TextColorRole:
            if hasattr(self, 'categories') and self.df.ix[index.row(), 'Deleted']:
                return QColor(*self.deleted_color_text)
            else:
                return DataFrameModel.data(self, index, role)
        else:
            if self.df.columns[index.column()] == 'Lastschrift' and role == Qt.DisplayRole:
                amount = self.df.ix[index.row(), index.column()]
                return QVariant(u'{:.2f} CHF'.format(amount))
            else:
                return DataFrameModel.data(self, index, role)

    #def setData(self, index, value, role):
        #if isinstance(value, unicode):
        #    value = value.encode('utf-8')
        #return DataFrameModel.setData(self, index, value, role)


class TransactionTableView(QtW.QTableView):
    def __init__(self, parent):
        QtW.QTableView.__init__(self, parent)
        self.setSortingEnabled(True)
        self.header = self.horizontalHeader()
        self.header.setStretchLastSection(True)
        self.n_pressed = 0
        self.last_key = None

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Space:
            if self.state() == self.EditingState:
                event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
                QtW.QTableView.keyPressEvent(self, event)
            else:
                self.edit(self.currentIndex())
        elif event.key() == Qt.Key_Return:
            event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
            QtW.QTableView.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Delete:
            index = self.currentIndex()
            model = self.model()
            smodel = model.sourceModel()
            sindex = model.mapToSource(index)
            c = smodel.i_deleted
            c_sindex = smodel.index(sindex.row(), c)
            index = model.mapFromSource(c_sindex)
            value = model.data(index, Qt.DisplayRole)
            model.setData(index, not eval(value), Qt.EditRole)
            for i in range(model.columnCount()):
                self.update(model.index(index.row(), i))
        elif event.text() <> "":
            t = event.text()
            index = self.currentIndex()
            model = self.model()
            smodel = model.sourceModel()
            sindex = model.mapToSource(index)
            categories = pd.Series(smodel.categories)
            cat = categories[categories.str.lower().str.startswith(t)]
            if len(cat) > 0:
                if t == self.last_key:
                    self.n_pressed += 1
                else:
                    self.n_pressed = 0
                if self.n_pressed >= len(cat):
                    self.n_pressed = 0
                cat = cat.iloc[self.n_pressed]
                c = smodel.i_categorie
                c_sindex = smodel.index(sindex.row(), c)
                index = model.mapFromSource(c_sindex)
                model.setData(index, cat, Qt.EditRole)
                for i in range(model.columnCount()):
                    self.update(model.index(index.row(), i))
                self.last_key = t
        else:
            QtW.QTableView.keyPressEvent(self, event)


class TransactionTable(DataFrameWidget):
    columns = ['Datum', 'Text', 'Lastschrift', 'Database', 'Deleted', 'Kategorie']
    widths = [80, 280, 130, 70, 60, 130]

    def __init__(self, data=pd.DataFrame(columns=['Datum', 'Text', 'Lastschrift', 'Database', 'Deleted', 'Kategorie']),
                 parent=None):

        QWidget.__init__(self, parent=parent)
        self.parent_ = parent
        self.dataModel = TransactionTableModel(data, self)
        self.dataTable = TransactionTableView(self)
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.dataModel)
        self.dataTable.setModel(self.proxy)
        self.dataTable.setItemDelegate(TransactionItemDelegate(self))

        self.dataTable.verticalHeader().setVisible(False)
        self.dataTable.setStyleSheet("selection-background-color: transparent; selection-color:black")

        self.dataTable.setSelectionBehavior(QtW.QTableView.SelectRows)
        self.dataTable.setEditTriggers(QtW.QTableView.SelectedClicked)
        self.dataTable.setWordWrap(True)

        # Set DataFrame
        self.initUI()

        # Set DataFrame
        self.setDataFrame(data)

    def initUI(self):
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QtW.QVBoxLayout()
        layout.addWidget(self.dataTable, 1)
        self.setLayout(layout)

    def setDataFrame(self, data):
        set_index = True
        if data is None:
            data = pd.DataFrame(columns=self.columns)
            set_index = False
        self.dataModel.setDataFrame(data)
        for i, dt in enumerate(data.dtypes):
            if self.dataModel.df.columns[i] == 'Kategorie':
                self.dataTable.setItemDelegateForColumn(i, TransactionComboBoxItemDelegate(self,
                                                                                           self.dataModel.categories + [
                                                                                               'nan']))
            elif data.ix[:, i].dtype == bool:
                self.dataTable.setItemDelegateForColumn(i, TransactionComboBoxItemDelegate(self, ['True', 'False']))
            # hide all but columns
            self.dataTable.showColumn(i)
            if data.columns[i] not in self.columns:
                self.dataTable.hideColumn(i)
        self.dataModel.signalUpdate()
        self.dataTable.resizeColumnsToContents()
        self.dataTable.resizeRowsToContents()

        self.i_cat = self.dataModel.i_categorie
        if set_index: self.dataTable.setCurrentIndex(self.proxy.mapFromSource(self.dataModel.index(0, self.i_cat)))
        self.dataTable.setColumnWidth(self.i_cat, 200)
        h = self.getMaxRowHeight()
        for i in range(self.dataModel.rowCount()):
            self.dataTable.setRowHeight(i, h)

        if set_index: self.dataTable.sortByColumn(self.dataModel.i_datum, Qt.AscendingOrder)
        self.setSizes()

    def setSizes(self):

        widths = iter(self.widths)
        for i in range(self.dataModel.columnCount()):
            if not self.dataTable.isColumnHidden(i):
                self.dataTable.setColumnWidth(i, widths.next())

        self.setFixedWidth(800)
        self.setMinimumHeight(400)


class TransactionItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):

        try:
            bg_color = index.data(Qt.BackgroundColorRole)
            painter.fillRect(option.rect, bg_color)
            QStyledItemDelegate.paint(self, painter, option, index)
        except TypeError:
            QStyledItemDelegate.paint(self, painter, option, index)


class TransactionComboBoxItemDelegate(TransactionItemDelegate, ComboBoxDelegate):
    pass
