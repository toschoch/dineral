#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

import sys, logging
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtGui import QIcon

import matplotlib as mpl
mpl.use('Qt5Agg')

import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from dataplugins import plugins

    from gui import FinanceMain

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-25s %(levelname)-8s %(message)s')

    log = logging.getLogger()

    app = QApplication(sys.argv)

    icon = QIcon(r'res/icon.png')
    trayIcon = QSystemTrayIcon(icon, app)

    app.setApplicationName('MyFinances')
    app.setWindowIcon(icon)

    log.info("Start program...")
    w = FinanceMain(plugins=plugins)
    w.show()

    sys.exit(app.exec_())
