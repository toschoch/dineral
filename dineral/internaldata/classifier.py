#!/usr/bin/env python
# encoding: utf-8
"""
classifier.py

Created by Tobias Schoch on 24.12.15.
Copyright (c) 2015. All rights reserved.
"""
import logging
import numpy as np
import pkg_resources
from builtins import str

from .property import Property

log = logging.getLogger(__name__)

class DummyClassifier(object):

    def __init__(self):
        self.classes_names = ['None']

    def predict(self,array):
        return np.zeros_like(array)


class Classifier(Property):
    TYPE = Property.FILE

    def __init__(self):
        Property.__init__(self)
        self._clf = None

    def read_clf(self,fname):
        import pickle, warnings
        with open(fname, 'rb') as fp:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                clf = pickle.load(fp)
        return clf

    def default_property(self):
        return 'res/classifiers/{}.pickle'.format(self._slugify(str(self._account)))

    def load(self):
        fname = self.properties
        # if pkg_resources.resource_exists('dineral',fname):
        #     fname = pkg_resources.resource_filename('dineral',fname)
        log.info("load classifier {}...".format(fname))

        try:
            clf = self.read_clf(fname)
        except IOError:
            log.warn('could not find a suitable classifier, create a dummy classifier...')
            clf = DummyClassifier()

        self._clf = clf
        return clf

    def date_training(self):
        try:
            return self._clf.TRAINING_DATE
        except AttributeError:
            return 'Unkown'

    def training_samples(self):
        try:
            return self._clf.TRAINING_SAMPLES
        except AttributeError:
            return 'Unkown'

    def test_samples(self):
        try:
            return self._clf.TEST_SAMPLES
        except AttributeError:
            return 'Unkown'

    def test_score(self):
        try:
            return ", ".join(map("{:.2f}".format, [self._clf.SCORE[i].mean() for i in range(3)]))
        except AttributeError:
            return 'Unkown'
