#!/usr/bin/env python
# encoding: utf-8
"""
classifier.py

Created by Tobias Schoch on 24.12.15.
Copyright (c) 2015. All rights reserved.
"""
import logging
import numpy as np

from property import Property

log = logging.getLogger(__name__)

class Classifier(Property):

    TYPE = Property.FILE

    def __init__(self):
        Property.__init__(self)
        self._clf = None

    def load(self):
        fname = self.properties
        log.info("load classifier {}...".format(fname))

        import pickle
        with open(fname,'rb') as fp:
            clf = pickle.load(fp)

        self._clf = clf
        return clf

    def predict(self, *args, **kwargs):
        self._clf.predict(*args, **kwargs)