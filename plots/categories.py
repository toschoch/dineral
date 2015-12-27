#!/usr/bin/env python
# encoding: utf-8
"""
categories.py

Created by Tobias Schoch on 27.12.15.
Copyright (c) 2015. All rights reserved.
"""

def plot_income(ax, data, category):

    linecolor='#5B9ECF'
    try:
        ax = data[category].plot(ax=ax,linewidth=2,color=linecolor,marker='o')
    except:
        return

    ax.fill_between(data.index,data[category],color=linecolor,alpha=0.6)

    pavg = ax.axhline(data[category].mean(),color='r',alpha=0.4,linewidth=2,linestyle='--')

    ax.set_title('Ausgaben '+category,size=12)
    # if budget is not None:
    #
    #     pbud, =plt.plot(category_data.Datum,np.repeat(-bud,len(category_data)),color='g',alpha=0.4,linewidth=2,linestyle='--')
    #     plt.legend([pavg,pbud],['Durchschnitt {0:.0f} CHF'.format(avg),'Budget {0:.0f} CHF'.format(-bud)],prop=fp)
    # else:
    ax.legend([pavg],['Average {0:.0f} CHF'.format(data[category].mean())])