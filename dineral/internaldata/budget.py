# encoding: utf-8
# -------------------------------------------------------------------------------
# Name:         budget
#
# Author:       tschoch
# Created:      04.12.2015
# Copyright:    (c) Sensirion AG 2015
# Licence:      all rights reserved.
# -------------------------------------------------------------------------------

__author__ = 'tschoch'
__copyright__ = '(c) Sensirion AG 2015'

""""""

import logging
import pandas as pd, os
import pyexcel_ods
import datetime
import seaborn as sns
from .property import CachedProperty
from builtins import str

log = logging.getLogger(__name__)


class Budget(CachedProperty):
    TYPE = CachedProperty.FILE

    def representation(self):
        path, filename = os.path.split(self.properties)
        path, year = os.path.split(path)
        location = os.path.join(path, '{year}')
        return os.path.join(location, filename)

    def load_data(self, year):
        fname = self.filename(year)
        data = pyexcel_ods.get_data(fname)
        data = data['Kategorien']
        columns = data.pop(0)
        data = pd.DataFrame(data, columns=columns)
        data['Kategorie'] = data['Kategorie'].astype(str)
        data['Kategorie'] = pd.Categorical(data['Kategorie'])
        data = data.set_index('Kategorie', drop=False)
        data.sort_index(inplace=True)
        data['colors'] = list(sns.color_palette("Set2", len(data)).as_hex())
        self._data = data
        self._year = year
        data.dropna(inplace=True)
        return data

    @property
    def date_from(self):
        return datetime.date(self._year, 1, 1)

    def filename(self, year):
        lastyear = year
        year = year + 1
        if year > 99:
            year = year % 100
        if lastyear > 99:
            lastyear = lastyear % 100

        path,filename = os.path.split(self.properties)
        path,_year = os.path.split(path)

        location = os.path.join(path, '{}{}'.format(lastyear, year))
        return os.path.join(location, filename)
