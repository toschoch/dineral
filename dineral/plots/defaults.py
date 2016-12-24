#!/usr/bin/env python
# encoding: utf-8
"""
defaults.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""

from matplotlib.dates import DateFormatter, DayLocator


def monthly_settings(ax):
    fmt = DateFormatter('%B')
    loc = DayLocator(bymonthday=1)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)

    ax.set_ylabel('Total Month [CHF]')

    for tick in ax.xaxis.get_majorticklabels(): tick.set_rotation(20)

    ylim = ax.get_ylim()
    if ylim[0] < 0:
        ylim = (ylim[0] * 1.2, ylim[1] * 1.2)
    else:
        ylim = (0, ylim[1] * 1.2)
    ax.set_ylim(ylim)
