# encoding: utf-8
#-------------------------------------------------------------------------------
# Name:         budget
#
# Author:       tschoch
# Created:      04.12.2015
# Copyright:    (c) Sensirion AG 2015
# Licence:      all rights reserved.
#-------------------------------------------------------------------------------

__author__ = 'tschoch'
__copyright__ = '(c) Sensirion AG 2015'

""""""

import logging
import pandas as pd, os
from property import Property

log = logging.getLogger(__name__)

class Budget(Property):

    TYPE = Property.DIR

    FILENAME = 'Budget.csv'

    def representation(self):
        location = os.path.join(self.properties,'{year}')
        return os.path.join(location,self.FILENAME)

    def load_data(self, year):
        fname = self.filename(year)
        return pd.read_csv(fname,delimiter=';',encoding='utf-8')

    def filename(self, year):
        lastyear=year-1
        if year>99:
            year=year%100
        if lastyear>99:
            lastyear=lastyear%100
        location = os.path.join(self.properties,'{}{}'.format(lastyear,year))
        return os.path.join(location,self.FILENAME)