#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------
# project: PyCharmProjects
# file:    test_import.py
# author:  tobi
# created: 24.12.16
# ----------------------------------
__author__ = 'tobi'
__copyright__ = 'Copyright TobyWorks, 2016'

import unittest


class Dineral(unittest.TestCase):
    def test_import(self):
        from dineral.main import main
        main()

if __name__ == '__main__':
    unittest.main()
