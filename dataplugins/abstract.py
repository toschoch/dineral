#!/usr/bin/env python
# encoding: utf-8
"""
abstract.py

Created by Tobias Schoch on 01.12.15.
Copyright (c) 2015. All rights reserved.
"""
import pandas as pd
import numpy as np

class LocationType(object):
    DIR = 1
    FILE = 0

_PROPERTIESFILE = 'properties.json'

class DataPlugin(LocationType):

    DEFAULTDATACOLUMNS = ['Datum','Text','Lastschrift','Kategorie']
    NOCATEGORY = np.NaN
    TYPE = LocationType.FILE

    LOAD = False

    def __init__(self):
        self.restore()

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def description(cls):
        return cls.__doc__.strip()

    @classmethod
    def type(cls):
        return cls.TYPE

    def store(self):
        import json,os
        path, _ = os.path.split(__file__)
        pFile = os.path.join(path,_PROPERTIESFILE)
        with open(pFile,'r') as fp:
            properties = json.load(fp)
        with open(pFile,'w+') as fp:
            properties[self.__class__.__name__] = self.properties
            json.dump(properties,fp,indent=2)

    def restore(self):
        import json,os
        path, _ = os.path.split(__file__)
        pFile = os.path.join(path,_PROPERTIESFILE)
        with open(pFile,'r') as fp:
            properties = json.load(fp)
            self.properties = properties[self.__class__.__name__]

    def load_data(self, period_from, period_to, callback=None):
        raise NotImplementedError()

