#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

import sys, logging, os
from PySide.QtGui import QApplication, QSystemTrayIcon, QIcon

import warnings
import matplotlib as mpl

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    warnings.filterwarnings("ignore", module="matplotlib")
    mpl.use('Qt4Agg')
    mpl.rcParams['backend.qt4'] = 'PySide'

    from gui import FinanceMain

def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-25s %(levelname)-8s %(message)s')

    log = logging.getLogger()

    app = QApplication(sys.argv)

    p=os.path.split(__file__)[0]
    p = os.path.join(p,r'res/dineral.png')
    icon = QIcon(p)
    trayIcon = QSystemTrayIcon(icon, app)

    app.setApplicationName('Dineral')
    app.setWindowIcon(icon)

    log.info("Start program...")
    w = FinanceMain()
    w.show()

    app.exec_()

if __name__ == '__main__':
    main()