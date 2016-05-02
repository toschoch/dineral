#!/usr/bin/env python
# encoding: utf-8
"""
style.py

Created by Tobias Schoch on 01.05.16.
Copyright (c) 2016. All rights reserved.
"""

import matplotlib as mpl

mpl.style.use(['seaborn-muted', 'seaborn-whitegrid'])
mpl.rcParams['grid.linestyle'] = ':'
mpl.rcParams['grid.color'] = '.8'
mpl.rcParams['legend.fancybox'] = True
mpl.rcParams['legend.frameon'] = True  # whether or not to draw a frame around legend
mpl.rcParams['legend.numpoints'] = 2  # whether or not to draw a frame around legend
mpl.rcParams['axes.grid'] = True
mpl.rcParams['axes.edgecolor'] = '0.5'
mpl.rcParams['image.cmap'] = 'viridis'
mpl.rcParams['legend.edgecolor'] = '0.5'
mpl.rcParams['figure.figsize'] = [8, 6]

contexts = dict(paper=1.0, notebook=1.3, talk=1.6, poster=1.9)


def set_context(context='paper', scaling=1.0):
    if context not in contexts.keys():
        raise ValueError("context must be in %s" % ", ".join(contexts))

    # Set up dictionary of default parameters
    base_context = {
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,

        "grid.linewidth": 1,
        "lines.linewidth": 1.75,
        "patch.linewidth": .3,
        "lines.markersize": 7,
        "lines.markeredgewidth": 0,

        "xtick.major.width": 1,
        "ytick.major.width": 1,
        "xtick.minor.width": .5,
        "ytick.minor.width": .5,

        "xtick.major.pad": 7,
        "ytick.major.pad": 7,
    }

    # Scale all the parameters by the same factor depending on the context
    scaling = scaling * contexts[context]
    context_dict = {k: v * scaling for k, v in base_context.items()}

    mpl.rcParams.update(context_dict)

    return context_dict


set_context('paper')
