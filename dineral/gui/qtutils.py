#!/usr/bin/env python
# encoding: utf-8
"""
qtutils.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""

from PyQt5 import QtWidgets as QtW
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDate


class QDateRange(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.dateFrom = QtW.QCalendarWidget(self)
        self.dateTo = QtW.QCalendarWidget(self)

        self.initUI()

    def initUI(self):
        grp = QtW.QGroupBox("Period:", self)
        layout = QtW.QGridLayout(self)

        layout.addWidget(QtW.QLabel("From", self), 0, 0)
        layout.addWidget(self.dateFrom, 1, 0)
        layout.addWidget(QtW.QLabel("To", self), 2, 0)
        layout.addWidget(self.dateTo, 3, 0)
        grp.setLayout(layout)

        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)


class QCheckBoxGroup(QWidget):
    def __init__(self, choices, title='Choices', parent=None):
        QWidget.__init__(self, parent)

        self.checkboxes = []
        for choice in choices:
            check = QtW.QCheckBox(choice, self)
            check.setChecked(True)
            self.checkboxes.append(check)
            setattr(self, choice, check)

        self.initUI(title)

    def initUI(self, title):
        grp = QtW.QGroupBox(title, self)
        layout = QtW.QGridLayout()
        for j, check in enumerate(self.checkboxes):
            i = (j / 4)
            j = (j % 4)
            layout.addWidget(check, i, j)
        grp.setLayout(layout)
        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)

    def checked(self):
        return [check.isChecked() for check in self.checkboxes]


class FinanceSelector(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.period = QDateRange(self)
        self.setStartDate()

        self.period.dateFrom.selectionChanged.connect(self.onDateSelected)
        self.period.dateTo.selectionChanged.connect(self.onDateSelected)

    def onDateSelected(self):

        sender = self.sender()

        date_to = self.period.dateTo.selectedDate()
        date_from = self.period.dateFrom.selectedDate()

        if date_from.year() != date_to.year():
            if sender is self.period.dateTo:
                self.period.dateFrom.setSelectedDate(QDate(date_to.year(), 1, 1))
            elif sender is self.period.dateFrom:
                self.period.dateTo.setSelectedDate(QDate(date_from.year(), 12, 31))

        if date_from > date_to:
            if sender is self.period.dateTo:
                self.period.dateFrom.setSelectedDate(QDate(date_to.year(), date_to.month(), 1))
            elif sender is self.period.dateFrom:
                self.period.dateTo.setSelectedDate(QDate(date_from.year(), date_from.month(), date_from.daysInMonth()))

    def initUI(self):
        raise NotImplementedError

    def setStartDate(self):
        raise NotImplementedError
