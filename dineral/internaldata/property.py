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
import json, os, yaml
import pkg_resources

log = logging.getLogger(__name__)

_CUSTOMCONFIG = '~/.dineral.yaml'
_CUSTOMCONFIG = os.path.expanduser(_CUSTOMCONFIG)

def assure_user_config():
    # create user configuration if not existing
    if not os.path.exists(_CUSTOMCONFIG) or not os.path.isfile(_CUSTOMCONFIG):
        if pkg_resources.resource_exists('dineral','res/conf/properties.json'):
            config = json.load(pkg_resources.resource_stream('dineral','res/conf/properties.json'))
        else:
            config = yaml.load(pkg_resources.resource_stream('dineral','res/conf/properties_template.yaml'))
        with open(_CUSTOMCONFIG,'w+') as fp:
            yaml.dump(config,fp, default_flow_style=False)

assure_user_config()

def load_config():
    with open(_CUSTOMCONFIG,'r') as fp:
        config = yaml.load(fp)
    return config

def save_config(config):
    with open(_CUSTOMCONFIG,'w') as fp:
        yaml.dump(config,fp, default_flow_style=False)

def accounts():
    config = load_config()
    config.keys()
    return {k:v.keys() for k,v in config.items()}


class LocationType(object):
    DIR = 1
    FILE = 0


class Property(LocationType):
    TYPE = LocationType.FILE

    _account = accounts().keys()[0]

    def __init__(self):
        self.restore()

    @classmethod
    def account(cls):
        return cls._account

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

    @staticmethod
    def _slugify(value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        import unicodedata, re
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        value = unicode(re.sub('[-\s]+', '-', value))
        return value

    def representation(self):
        return unicode(self.properties)

    def default_property(self):
        log.error('No default property defined for "{}"...'.format(self.__class__.__name__))
        raise NotImplementedError()

    def store(self):
        config = load_config()
        config[self._account][self.__class__.__name__] = self.properties
        save_config(config)
        log.info(u"stored property for account {}: {} -> {}".format(self._account,self.__class__.__name__, self.properties))

    def restore(self):
        config = load_config()
        if config[self._account].has_key(self.__class__.__name__):
            self.properties = config[self._account][self.__class__.__name__]
        else:
            self.properties = self.default_property()
            self.store()
        log.info(u"restored property for account {}: {} -> {}".format(self._account,self.__class__.__name__, self.properties))


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


