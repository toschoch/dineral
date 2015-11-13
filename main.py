#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Tobias Schoch on 11.11.15.
Copyright (c) 2015. All rights reserved.
"""

import sys
from PyQt5.QtWidgets import QApplication

from gui import FinanceMain


if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = FinanceMain()
    w.show()

    sys.exit(app.exec_())