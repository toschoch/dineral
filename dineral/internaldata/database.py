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
        fname = self.filename(False)
        empty = pd.DataFrame(columns=["Datum","Deleted","Hash","Kategorie","Lastschrift","Text"])
        empty.to_feather(fname)

    def default_property(self):
        fname = 'res/data/{}.feather'.format(self._slugify(str(self._account)))
        return fname

    def read_data(self,fname):
        data = pd.read_feather(fname)
        return data

    def load_data(self):
        import numpy as np
        try:
            fname = self.filename(self.FROM_BACKUP)
            log.info("load database from {}...".format(fname))
            data = pd.read_feather(fname)
        except IOError as err:
            log.error(str(err))
            fname = self.filename(True)
            log.info("load database from {}...".format(fname))
            try:
                data = self.read_data(fname)
            except IOError:
                log.info("No database found... create a blank database")
                self.create_blank_db()
                fname = self.filename(False)
                self.FROM_BACKUP = False
                data = self.read_data(fname)

        if self.BACKUP and not self.FROM_BACKUP:
            log.debug("Save a backup copy of the database...")
            self.save_data(data, backup=True)

        data.Text = data.Text.str.replace('\\', '\n')
        data.Text = data.Text.str.replace('\n\n', '\n')
        data.ix[data.Deleted, 'Kategorie'] = np.nan

        if 'Unterkategorie' in data.columns:
            del data['Unterkategorie']

        # make categories
        import datetime
        data.Datum = data.Datum.apply(lambda x: datetime.date(x.year, x.month, x.day))
        data.Kategorie = pd.Categorical(data.Kategorie)
        self._data = data
        return data

    def add_categories(self,categories):
        data = self.data
        newcats = pd.Index(categories).difference(data.Kategorie.cat.categories)
        if len(newcats)>0:
            data['Kategorie'] = data.Kategorie.cat.add_categories(newcats)
        self._data = data

    def save_data(self, data, backup=False):
        data = data.reset_index(drop=True)
        if backup and self.FROM_BACKUP:
            raise Warning("Database was loaded from backup. Potential dataloss!!")
        fname = self.filename(backup)
        data.Text = data.Text.str.replace('\n', '\\\\')

        log.info("saved database to {}...".format(fname))
        data.to_csv(fname, index=False, encoding='utf-8', sep=';', mode='w+')
        data.Kategorie = pd.Categorical(data.Kategorie)
        self._data = data

    def filename(self, backup=False):
        if not backup:
            fname =  self.properties
        else:
            fname, ext = os.path.splitext(self.properties)
            fname = "{}_backup{}".format(fname, ext)
        #if pkg_resources.resource_exists('dineral',fname):
        #    fname = pkg_resources.resource_filename('dineral',fname)
        return fname