#!/usr/bin/env python
# encoding: utf-8
"""
database.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
import logging
import pandas as pd, os
from property import Property

log = logging.getLogger(__name__)

class Database(Property):

    TYPE = Property.FILE
    FROM_BACKUP = False
    BACKUP = True

    def load_data(self):
        fname = self.filename(self.FROM_BACKUP)
        log.info("load database from {}...".format(fname))
        data = pd.read_csv(fname,delimiter=";")
        if self.BACKUP and not self.FROM_BACKUP:
            log.debug("Save a backup copy of the database...")
            self.save_data(data, backup=True)

        # make categories
        data.Kategorie = pd.Categorical(data.Kategorie)
        return data

    def save_data(self, data, backup=False):
        if backup and self.FROM_BACKUP:
            raise Warning("Database was loaded from backup. Potential dataloss!!")
        fname = self.filename(backup)
        data.to_csv(fname)

    def filename(self, backup=False):
        if not backup:
            return self.properties
        else:
            fname, ext = os.path.splitext(self.properties)
            fname = "{}_backup{}".format(fname,ext)
            return fname