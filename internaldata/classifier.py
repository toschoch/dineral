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

        import pickle, warnings
        with open(fname, 'rb') as fp:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                clf = pickle.load(fp)

        self._clf = clf
        return clf

    def predict(self, *args, **kwargs):
        self._clf.predict(*args, **kwargs)

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
