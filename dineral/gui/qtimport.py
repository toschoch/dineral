# encoding: utf-8
# -------------------------------------------------------------------------------
# Name:         qtimport
#
# Author:       tschoch
# Created:      02.12.2015
# Copyright:    (c) Sensirion AG 2015
# Licence:      all rights reserved.
# -------------------------------------------------------------------------------

__author__ = 'tschoch'
__copyright__ = '(c) Sensirion AG 2015'

""""""

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QProgressDialog

from builtins import str

import pandas as pd
import logging

log = logging.getLogger(__name__)


class DataImport(QProgressDialog):
    success = pyqtSignal(pd.DataFrame)

    def __init__(self, plugins, parent=None):
        QProgressDialog.__init__(self, None)
        self.setAutoClose(False)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.plugins = plugins
        self.setWindowTitle('Import Data')
        self.setValue(100)

    def start(self, period_from, period_to):
        kwargs = {'period_from': period_from, 'period_to': period_to}
        process = ImportProcess(self.plugins, self.success, parent=self, **kwargs)
        process.progressNotify.connect(self.setValue)
        process.progesssLabel.connect(self.setLabelText)
        process.progressClose.connect(self.cancel)
        process.setTerminationEnabled(True)
        self.canceled.connect(process.terminate)
        self.setValue(0)
        # self.forceShow()
        process.start()


class ImportProcess(QThread):
    progressNotify = pyqtSignal(int)
    progesssLabel = pyqtSignal(str)
    progressClose = pyqtSignal()

    def __init__(self, plugins, success, parent=None, **kwargs):
        QThread.__init__(self, parent)
        self.setTerminationEnabled(True)
        self.plugins = plugins
        self.success = success
        self.kwargs = kwargs

    def run(self):
        log.info("Importer started")
        data = []
        for plugin in self.plugins:
            if not plugin.LOAD: continue
            log.info("load {}...".format(plugin.name()))
            self.progesssLabel.emit(plugin.description() + '...')
            d = plugin.load_data(callback=self.progressNotify.emit, **self.kwargs)
            data.append(d)

            self.progressNotify.emit(0)
        self.progressClose.emit()
        if len(data) > 0:
            data = pd.concat(data, axis=0)
            data.reset_index(inplace=True, drop=True)
            if not data.empty:
                log.info("Data successfully imported! ({} entries)".format(len(data)))
                self.success.emit(data)
        else:
            log.info("No data found for the selected period!")
