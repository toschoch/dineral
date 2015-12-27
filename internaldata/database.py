#!/usr/bin/env python
# encoding: utf-8
"""
database.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
import logging
import pandas as pd, os
from property import CachedProperty

log = logging.getLogger(__name__)

class Database(CachedProperty):

    TYPE = CachedProperty.FILE
    FROM_BACKUP = False
    BACKUP = True

    def load_data(self):
        import numpy as np
        fname = self.filename(self.FROM_BACKUP)
        log.info("load database from {}...".format(fname))
        data = pd.read_csv(fname,delimiter=";",parse_dates=['Datum'],dayfirst=True)
        if self.BACKUP and not self.FROM_BACKUP:
            log.debug("Save a backup copy of the database...")
            self.save_data(data, backup=True)

        data.Text = data.Text.str.replace('\\','\n')
        data.Text = data.Text.str.replace('\n\n','\n')
        data.ix[data.Deleted,'Kategorie']=np.nan

        if 'Unterkategorie' in data.columns:
            del data['Unterkategorie']

        # make categories
        import datetime
        data.Datum = data.Datum.apply(lambda x: datetime.date(x.year,x.month,x.day))
        data.Kategorie = pd.Categorical(data.Kategorie)
        self._data = data
        return data

    def save_data(self, data, backup=False):
        data = data.reset_index(drop=True)
        if backup and self.FROM_BACKUP:
            raise Warning("Database was loaded from backup. Potential dataloss!!")
        fname = self.filename(backup)
        data.Text = data.Text.str.replace('\n','\\\\')

        log.info("saved database to {}...".format(fname))
        data.to_csv(fname,index=False,encoding='utf-8',sep=';',mode='w+')
        self._data = data

    def filename(self, backup=False):
        if not backup:
            return self.properties
        else:
            fname, ext = os.path.splitext(self.properties)
            fname = "{}_backup{}".format(fname,ext)
            return fname