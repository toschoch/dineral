#!/usr/bin/env python
# encoding: utf-8
"""
cover.py

Created by Tobias Schoch on 01.01.16.
Copyright (c) 2016. All rights reserved.
"""

from __future__ import unicode_literals

from .abstract_plot import Plot
from ..internaldata.property import Property


class Cover(Plot):
    def plot(self, data, budget, ax, start, stop, *args):
        ax.set_frame_on(False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        text = u'Report Dineral\n"{}"'.format(Property.account())
        text += '\n\n'
        text += start.strftime('%d. %B %Y')
        text += " bis "
        text += stop.strftime(u'%d. %B %Y')
        ax.text(0.5, 0.5, text, transform=ax.transAxes, fontweight='bold', va='center', ha='center')
