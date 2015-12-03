# encoding: utf-8
#-------------------------------------------------------------------------------
# Name:         qtinfo.py
#
# Author:       tschoch
# Created:      02.12.2015
# Copyright:    (c) Sensirion AG 2015
# Licence:      all rights reserved.
#-------------------------------------------------------------------------------

__author__ = 'tschoch'
__copyright__ = '(c) Sensirion AG 2015'

""""""

import logging

log = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

class Info(QtGui.QDialog):

    def __init__(self, info, header, title='Info', parent=None):
        QtGui.QDialog.__init__(self,parent)

        layout = QtGui.QVBoxLayout()

        grp = QtGui.QGroupBox(header, self)
        grplayout = QtGui.QGridLayout()

        for i,item in enumerate(info):
            for j,txt in enumerate(item):
                lbl = QtGui.QLabel(txt,self)
                lbl.setWordWrap(True)
                lbl.setAlignment(QtCore.Qt.AlignTop)
                grplayout.addWidget(lbl,i,j)

        grp.setLayout(grplayout)

        layout.addWidget(grp)

        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok,parent=parent)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.close)

        layout.setSizeConstraint(layout.SetFixedSize)
        self.setLayout(layout)

        self.setWindowTitle(title)

