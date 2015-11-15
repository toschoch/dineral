# -- coding: utf-8 --
from dateutil.relativedelta import relativedelta

__author__ = 'tobi'

def lastOf(what,date):
    """ returns the last of date. e.g. what='hour' returns the last minute after date
    """
    date = firstOf(what,date+relativedelta(**dict([(what+'s',1)])))
    return date - relativedelta(microseconds=1)

def firstOf(what,date):
    """ returns the first of date. e.g. what='hour' returns the first minute before date
    """
    fields=['year','month','day']
    values=[1,1,1,0,0,0,0]
    i = fields.index(what)
    kwargs=dict(zip(fields[i+1:],values[i+1:]))
    return date.replace(**kwargs)