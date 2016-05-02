#!/usr/bin/env python
# encoding: utf-8
"""
abstract.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""

import logging

log = logging.getLogger(__name__)


class Plot(object):
    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def description(cls):
        return cls.__doc__.strip()

    @classmethod
    def page(cls):
        raise NotImplementedError
