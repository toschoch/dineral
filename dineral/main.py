#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

import sys, logging, os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtGui import QIcon
import pkg_resources

from dineral.gui.qtmain import FinanceMain
from dineral.version import __version__

import warnings
import matplotlib as mpl

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    warnings.filterwarnings("ignore", module="matplotlib")
    mpl.use('Qt5Agg')
    #mpl.rcParams['backend.qt4'] = 'PyQt5'


def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-25s %(levelname)-8s %(message)s')

    log = logging.getLogger()

    app = QApplication(sys.argv)

    try:
        p = pkg_resources.resource_filename('dineral','res/dineral.png')
    except:
        p=os.path.split(__file__)[0]
        p = os.path.join(p,r'res/dineral.png')
    icon = QIcon(p)
    trayIcon = QSystemTrayIcon(icon, app)

    app.setApplicationName('Dineral')
    app.setWindowIcon(icon)

    log.info("Start program (version={})...".format(__version__))
    w = FinanceMain(version=__version__)
    w.show()

    app.exec_()

if __name__ == '__main__':
    main()