# encoding: utf-8
# -------------------------------------------------------------------------------
# Name:         property
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
import contextlib, os

log = logging.getLogger(__name__)


class LocationType(object):
    DIR = 1
    FILE = 0


_PROPERTIESFILE = 'properties.json'


class Property(LocationType):
    TYPE = LocationType.FILE

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

    def __str__(self):
        return self.representation()

    def representation(self):
        return unicode(self.properties)

    def store(self):
        import json, os
        path, _ = os.path.split(__file__)
        pFile = os.path.join(path, _PROPERTIESFILE)
        with open(pFile, 'r') as fp:
            properties = json.load(fp)
        with open(pFile, 'w+') as fp:
            properties[self.__class__.__name__] = self.properties
            json.dump(properties, fp, indent=2)
            log.info(u"stored property for {}: {}".format(self.__class__.__name__, self.properties))

    def restore(self):
        import json, os
        path, _ = os.path.split(__file__)
        pFile = os.path.join(path, _PROPERTIESFILE)
        with open(pFile, 'r') as fp:
            properties = json.load(fp)
            self.properties = properties[self.__class__.__name__]
            log.info(u"restored property for {}: {}".format(self.__class__.__name__, self.properties))

    @staticmethod
    @contextlib.contextmanager
    def set_relativepath():
        curdir = os.getcwd()
        os.chdir(os.path.split(__file__)[0])
        try:
            yield
        finally:
            os.chdir(curdir)


class CachedProperty(Property):
    def __init__(self):
        Property.__init__(self)
        self._data = None

    @property
    def data(self, *args, **kwargs):
        if self._data is None:
            self._data = self.load_data(*args, **kwargs)
        return self._data

    def load_data(self, *args, **kwargs):
        raise NotImplementedError


