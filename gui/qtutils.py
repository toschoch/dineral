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

class QInfo(QWidget):

    year = None
    nentries = 0

    __labels = []

    def __init__(self,label="",parent=None):
        QWidget.__init__(self,parent)

        self.header = QtW.QLabel(self.linespaced("Budget:<br>Database:<br>Classifier:"),self)
        self.label = QtW.QLabel(label,self)
        self._add_label(self.label)

        self.initUI()

    def initUI(self):
        grp = QtW.QGroupBox("Info:",self)
        layout = QtW.QHBoxLayout()

        layout.addWidget(self.header,stretch=0)
        layout.addWidget(self.label,stretch=1)
        grp.setLayout(layout)

        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)

    @staticmethod
    def linespaced(text):
        return '<p style="line-height:{}">{}<p>'.format(120,text)

    @classmethod
    def _add_label(cls,label):
        cls.__labels.append(label)

    @classmethod
    def set_info(cls, year=None, nentries=None):
        if not year:
            year = cls.year
        cls.year = year
        if not nentries:
            nentries = cls.nentries
        cls.nentries = nentries

        text = "loaded for year {} according to selected period<br>".format(cls.year)
        text+= "loaded {} entries<br>".format(cls.nentries)
        text+= "loaded"

        text = cls.linespaced(text)
        for label in cls.__labels:
            label.setText(text)




class QDateRange(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)

        self.dateFrom = QtW.QCalendarWidget(self)
        self.dateTo = QtW.QCalendarWidget(self)

        self.initUI()

    def initUI(self):
        grp = QtW.QGroupBox("Period:",self)
        layout = QtW.QGridLayout(self)

        layout.addWidget(QtW.QLabel("From",self),0,0)
        layout.addWidget(self.dateFrom,1,0)
        layout.addWidget(QtW.QLabel("To",self),0,1)
        layout.addWidget(self.dateTo,1,1)
        grp.setLayout(layout)

        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)

class QCheckBoxGroup(QWidget):

    def __init__(self, choices, title='Choices', parent=None):
        QWidget.__init__(self, parent)

        self.checkboxes = []
        for choice in choices:
            check = QtW.QCheckBox(choice,self)
            check.setChecked(True)
            self.checkboxes.append(check)
            setattr(self,choice,check)

        self.initUI(title)

    def initUI(self, title):
        grp = QtW.QGroupBox(title,self)
        layout = QtW.QGridLayout()
        for j,check in enumerate(self.checkboxes):
            i = (j/4)
            j = (j%4)
            layout.addWidget(check,i,j)
        grp.setLayout(layout)
        layout = QtW.QHBoxLayout(self)
        layout.addWidget(grp)
        self.setLayout(layout)

    def checked(self):
        return [check.isChecked() for check in self.checkboxes]

class FinanceSelector(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self,parent)

        self.period = QDateRange(self)
        self.info = QInfo(parent=self)

        self.period.dateFrom.selectionChanged.connect(self.onDateSelected)
        self.period.dateTo.selectionChanged.connect(self.onDateSelected)

    def onDateSelected(self):
        date_to = self.period.dateTo.selectedDate()
        date_from = self.period.dateFrom.selectedDate()
        firstDay = QDate(date_to.year(),1,1)
        if firstDay>date_from:
            self.period.dateFrom.setSelectedDate(firstDay)

        selected_year = date_to.year()
        window = self.window()
        window.budget_data = window.budget.load_data(selected_year)
        self.info.set_info(year=selected_year)

    def initUI(self):
        raise NotImplementedError
    def setStartDate(self):
        raise NotImplementedError