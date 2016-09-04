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

from PySide import QtCore
from PySide.QtGui import QDialog, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QDialogButtonBox


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
