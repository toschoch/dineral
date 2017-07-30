#!/usr/bin/env python
# encoding: utf-8
"""
report.py

Created by Tobias Schoch on 01.01.16.
Copyright (c) 2016. All rights reserved.
"""
import logging
import numpy as np
from property import Property

log = logging.getLogger(__name__)



class Report(Property):
    TYPE = Property.FILE


    def default_property(self):
        return '~/Report_Dineral_{}.pdf'.format(self._slugify(unicode(self._account)))


class Data(Property):
    TYPE = Property.DIR


    def default_property(self):
        return '~/dineral_data_{}.csv'.format(self._slugify(unicode(self._account)))
