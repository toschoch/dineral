# -- coding: utf-8 --
import pandas as pd

__author__ = 'tobi'

def save_data(filename,data,delimiter=';',**kwargs):
    """ saves data in a recarray to a file
    """
    data.to_csv(filename,delimiter=delimiter,encoding=kwargs.pop('encoding','utf-8'),**kwargs)


def load_data(filename,delimiter=';',**kwargs):
    """ loads a recarray
    """

    return pd.read_csv(filename,delimiter=delimiter,encoding=kwargs.pop('encoding','utf-8'),**kwargs)