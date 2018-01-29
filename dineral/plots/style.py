#!/usr/bin/env python
# encoding: utf-8
"""
style.py

Created by Tobias Schoch on 01.05.16.
Copyright (c) 2016. All rights reserved.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import pkg_resources


def set_style(style):

    plt.rcParams.update(plt.rcParamsDefault)

    fname = pkg_resources.resource_filename("dineral","res/{}.style".format(style))
    plt.style.use(fname)

    # mpl.rcParams['grid.linestyle'] = ':'
    # mpl.rcParams['grid.color'] = '.8'
    # mpl.rcParams['legend.fancybox'] = True
    # mpl.rcParams['legend.frameon'] = True  # whether or not to draw a frame around legend
    # mpl.rcParams['legend.numpoints'] = 2  # whether or not to draw a frame around legend
    # mpl.rcParams['axes.grid'] = True
    # mpl.rcParams['axes.edgecolor'] = '0.5'
    # mpl.rcParams['image.cmap'] = 'viridis'
    # mpl.rcParams['legend.edgecolor'] = '0.5'
    # mpl.rcParams['figure.figsize'] = [8, 6]
