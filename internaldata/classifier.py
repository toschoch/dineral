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

    def load(self):
        fname = self.properties
        log.info("load classifier {}...".format(fname))

        import pickle
        with open(fname,'rb') as fp:
            clf = pickle.load(fp)

        clf.classes_names = np.array(map(lambda s:s.encode('utf-8'), clf.classes_names),dtype='object')
        return clf