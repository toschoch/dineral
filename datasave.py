# -- coding: utf-8 --
import pandas as pd

__author__ = 'tobi'

def save_data(filename,data,delimiter=';'):
    """ saves data in a recarray to a file
    """
    data.to_csv(filename,delimiter=delimiter)


def load_data(filename,delimiter=';'):
    """ loads a recarray
    """

    return pd.read_csv(filename,delimiter=delimiter)