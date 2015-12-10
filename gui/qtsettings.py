# encoding: utf-8
#-------------------------------------------------------------------------------
# Name:         qtsettings
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

from PyQt5 import QtCore
import PyQt5.QtWidgets as QtGui

class DataPluginProperty(QtGui.QWidget):

    def __init__(self, plugin, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.plugin = plugin

        layout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel("{}:".format(plugin.name()),self)
        layout.addWidget(self.label,0)
        self.line = QtGui.QLineEdit(plugin.properties,self)
        self.line.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.line.setReadOnly(True)
        layout.addWidget(self.line,1)
        button = QtGui.QPushButton('choose',self)
        button.clicked.connect(self.choose)
        layout.addWidget(button,0)

        self.setLayout(layout)

    def choose(self):

        old = self.plugin.properties
        if self.plugin.type()==self.plugin.FILE:
            new, _ = QtGui.QFileDialog.getOpenFileName(self,"Select {} location".format(self.plugin.name()))
        elif self.plugin.type()==self.plugin.DIR:
            new = QtGui.QFileDialog.getExistingDirectory(self,"Select {} location".format(self.plugin.name()),old)
        else:
            return
        if new == '': return

        self.plugin.properties = new
        self.plugin.store()
        self.line.setText(new)


class Settings(QtGui.QDialog):

    def __init__(self, plugins, internal, parent=None):
        QtGui.QDialog.__init__(self, parent)

        layout = QtGui.QVBoxLayout()

        sources = QDataPluginsSettings(plugins,'Sources',self)
        internal = QDataPluginsSettings(internal,'Internal',self)

        layout.addWidget(sources)
        layout.addWidget(internal)

        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok,parent=parent)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.close)

        layout.setSizeConstraint(layout.SetFixedSize)
        self.setLayout(layout)

        self.setWindowTitle('Settings')

class QDataPluginsSettings(QtGui.QGroupBox):

    def __init__(self, plugins, title, parent = None):
        QtGui.QGroupBox.__init__(self, title, parent)
        layout = QtGui.QVBoxLayout()
        self.props = []
        for plugin in plugins:
            prop = DataPluginProperty(plugin,parent=self)
            self.props.append(prop)
            layout.addWidget(prop)

        layout.setSpacing(0)
        self.setLayout(layout)
        w = self.GetlabelWidth()
        self.SetlabelWidth(w)
        self.SetEditWidth(300)

    def GetlabelWidth(self):
        return max([p.label.width() for p in self.props])

    def SetlabelWidth(self, width):
        for p in self.props:
            p.label.setFixedWidth(width)

    def SetEditWidth(self, width):
        for p in self.props:
            p.line.setFixedWidth(width)