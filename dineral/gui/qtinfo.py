# encoding: utf-8
# -------------------------------------------------------------------------------
# Name:         qtinfo.py
#
# Author:       tschoch
# Created:      02.12.2015
# Copyright:    (c) Sensirion AG 2015
# Licence:      all rights reserved.
# -------------------------------------------------------------------------------

__author__ = 'tschoch'
__copyright__ = '(c) Sensirion AG 2015'

""""""

import logging

log = logging.getLogger(__name__)

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QDialogButtonBox, QHBoxLayout, QComboBox


class Info(QDialog):
    def __init__(self, info, header, title='Info', parent=None):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()

        grp = QGroupBox(header, self)
        grplayout = QGridLayout()

        for i, item in enumerate(info):
            for j, txt in enumerate(item):
                lbl = QLabel(txt, self)
                lbl.setWordWrap(True)
                lbl.setAlignment(QtCore.Qt.AlignTop)
                grplayout.addWidget(lbl, i, j)

        grp.setLayout(grplayout)

        layout.addWidget(grp)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok, parent=parent)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.close)

        layout.setSizeConstraint(layout.SetFixedSize)
        self.setLayout(layout)

        self.setWindowTitle(title)


class AccountSelector(QDialog):
    def __init__(self, accounts, title='Select Account...', parent=None):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()
        line = QHBoxLayout()

        lbl =  QLabel('Account',self)
        self.selectAccount = QComboBox(self)
        self.selectAccount.addItems(accounts)
        line.addWidget(lbl)
        line.addWidget(self.selectAccount)
        layout.addLayout(line)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok, parent=parent)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.close)

        layout.setSizeConstraint(layout.SetFixedSize)
        self.setLayout(layout)

        self.setWindowTitle(title)