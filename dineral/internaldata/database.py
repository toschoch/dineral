#!/usr/bin/env python
# encoding: utf-8
"""
database.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
import logging
import pandas as pd, os
from .property import CachedProperty
import pkg_resources
from builtins import str

log = logging.getLogger(__name__)


class Database(CachedProperty):
    TYPE = CachedProperty.FILE
    FROM_BACKUP = False
    BACKUP = True

    def get_size(self):
        return os.path.getsize(self.properties)

    def create_blank_db(self):
        fname = self.properties
        empty = pd.DataFrame([[pd.to_datetime("1-1-1971"),True,'xxx','Deleted',0,'Dummy']],
                             columns=["Datum","Deleted","Hash","Kategorie","Lastschrift","Text"])
        empty['Kategorie'] = empty.Kategorie.astype('category')
        empty.to_feather(fname)

    def default_property(self):
        fname = 'res/data/{}.feather'.format(self._slugify(str(self._account)))
        return fname

    def read_data(self,fname):
        data = pd.read_feather(fname)
        return data

    def load_data(self):

        try:
            fname = self.properties
            log.info("load database from {}...".format(fname))
            data = pd.read_feather(fname)
        except IOError as err:
            log.error(str(err))
            log.info("Database not found... create a blank database")
            self.create_blank_db()
            fname = self.properties
            data = self.read_data(fname)

        self._data = data
        return data

    def add_categories(self, categories):
        data = self.data
        newcats = pd.Index(categories).difference(data.Kategorie.cat.categories)
        if len(newcats)>0:
            data['Kategorie'] = data.Kategorie.cat.add_categories(newcats)
        self._data = data

    def save_data(self, data):
        data = data.reset_index(drop=True)
        data['Kategorie'] = data.Kategorie.astype('category')

        fname = self.properties

        log.info("saved database to {}...".format(fname))
        data.to_feather(fname)