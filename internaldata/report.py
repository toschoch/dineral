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