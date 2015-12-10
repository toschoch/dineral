# encoding: utf-8
#-------------------------------------------------------------------------------
# Name:         abstract.py
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

import numpy as np

from internaldata import Property

log = logging.getLogger(__name__)

class DataPlugin(Property):

    DEFAULTDATACOLUMNS = ['Datum','Text','Lastschrift','Kategorie']
    NOCATEGORY = np.NaN

    def load_data(self, period_from, period_to, callback=None):
        raise NotImplementedError()

