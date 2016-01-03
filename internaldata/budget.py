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
import datetime
import seaborn as sns
from property import CachedProperty

log = logging.getLogger(__name__)

class Budget(CachedProperty):

    TYPE = CachedProperty.DIR

    FILENAME = 'Budget.csv'

    def representation(self):
        location = os.path.join(self.properties,'{year}')
        return os.path.join(location,self.FILENAME)

    def load_data(self, year):
        fname = self.filename(year)
        data = pd.read_csv(fname,delimiter=';',encoding='utf-8')
        data['Kategorie']=data['Kategorie'].astype(unicode)
        data['Kategorie']=pd.Categorical(data['Kategorie'])
        data = data.set_index('Kategorie',drop=False)
        data.sort_index(inplace=True)
        data['colors']=list(sns.color_palette("Set2",len(data)).as_hex())
        self._data = data
        self._year = year
        return data

    @property
    def date_from(self):
        return datetime.date(self._year,1,1)

    def filename(self, year):
        lastyear=year-1
        if year>99:
            year=year%100
        if lastyear>99:
            lastyear=lastyear%100
        location = os.path.join(self.properties,'{}{}'.format(lastyear,year))
        return os.path.join(location,self.FILENAME)