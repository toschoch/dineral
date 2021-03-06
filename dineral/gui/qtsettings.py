# encoding: utf-8
# -------------------------------------------------------------------------------
# Name:         qtsettings
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

import PyQt5.QtWidgets as QtGui
from PyQt5.QtGui import QFont, QFontMetrics


class DataPluginProperty(QtGui.QWidget):
    def __init__(self, plugin, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.plugin = plugin

        layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel("{}:".format(plugin.name()), self)
        layout.addWidget(self.label, 0)
        self.line = QtGui.QLineEdit(plugin.representation(), self)
        self.line.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.line.setReadOnly(True)
        layout.addWidget(self.line, 1)
        button = QtGui.QPushButton('choose', self)
        button.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.MinimumExpanding))
        button.clicked.connect(self.choose)
        layout.addWidget(button, 0)

        self.setLayout(layout)

    def lineWidth(self):
        font = QFont("", 0)
        fm = QFontMetrics(font)
        text = self.line.text()
        return fm.width(text)

    def choose(self):

        old = self.plugin.properties
        if self.plugin.type() == self.plugin.FILE:
            new, _ = QtGui.QFileDialog.getSaveFileName(self, "Select {} location".format(self.plugin.name()))
        elif self.plugin.type() == self.plugin.DIR:
            new = QtGui.QFileDialog.getExistingDirectory(self, "Select {} location".format(self.plugin.name()), old)
        else:
            return
        if new == '': return

        self.plugin.properties = new
        self.plugin.store()
        self.line.setText(new)


class Settings(QtGui.QDialog):
    def __init__(self, parent=None, **kwargs):
        QtGui.QDialog.__init__(self, parent)

        layout = QtGui.QVBoxLayout()

        order = ['sources', 'output', 'internal']
        additional = list(set(kwargs.keys()) - set(order))

        for i, k in enumerate(order + additional):
            v = kwargs.pop(k)
            w = QDataPluginsSettings(v, k, self)
            setattr(self, k, w)
            if i == 0:
                _width = w.SetOptimalEditWidth()
                _lbl = w.GetlabelWidth()
            else:
                w.SetlabelWidth(_lbl)
                w.SetEditWidth(_width)

            layout.addWidget(w)

        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, parent=parent)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.close)

        layout.setSizeConstraint(layout.SetFixedSize)
        self.setLayout(layout)

        self.setWindowTitle('Settings')

    def close(self):
        for property in self.internal.props:
            if property.plugin.name() == 'Database':
                property.plugin.load_data()
        return QtGui.QDialog.close(self)


class QDataPluginsSettings(QtGui.QGroupBox):
    def __init__(self, plugins, title, parent=None):
        QtGui.QGroupBox.__init__(self, title, parent)
        layout = QtGui.QVBoxLayout()
        self.props = []
        for plugin in plugins:
            prop = DataPluginProperty(plugin, parent=self)
            self.props.append(prop)
            layout.addWidget(prop)

        layout.setSpacing(0)
        self.setLayout(layout)
        w = self.GetlabelWidth()
        self.SetlabelWidth(w)

    def GetlabelWidth(self):
        return max([p.label.width() for p in self.props]+[300])

    def SetlabelWidth(self, width):
        for p in self.props:
            p.label.setFixedWidth(width)

    def GetOptimalEditWidth(self):
        return max([p.lineWidth() for p in self.props]+[300])

    def SetOptimalEditWidth(self):
        w = self.GetOptimalEditWidth()
        self.SetEditWidth(w)
        return w

    def SetEditWidth(self, w):
        for p in self.props:
            p.line.setFixedWidth(w)
