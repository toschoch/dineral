# -- coding: utf-8 --
__author__ = 'tobi'

import numpy as np
import glob, os
from dataload import *
import numpy.lib.recfunctions as recfun

confirmation_path = ur'/home/tobi/Finance/Konto Dokumente/Kontos Post/Zahlungsbestätigungen'
extract_path = ur'/home/tobi/Finance/Konto Dokumente/Kontos Post/Konto Auszüge Postkonto'


def expand_EFinance(data):
    """ expand all unspecific E-Finance entries with the corresponding entries from the payment confirmation

        Parameters
        ----------
        data:           (numpy.rec.recarray) table with data

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    I = np.char.array(data['Text']).startswith('E-FINANCE AUFTRAG')

    new = []
    for row in data[I]:

        try:
            pdffile = glob.glob(os.path.join(confirmation_path, row['Datum'].strftime('%Y-%m-%d') + u'.pdf'))[0]
            newrows = load_PostFinancePaymentConfirmation(pdffile)
            new.append(newrows)
        except IndexError:
            pass

    new.append(data[np.logical_not(I)])

    new = recfun.stack_arrays(new, autoconvert=True)

    return new


def load_PostFinanceData(datum,data=None):
    """ load all data from postfinance account extracts

        Parameters
        ----------
        datum:           (str) datum from when the data shall be loaded e.g. '01-01-2014'

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    if data is not None:
        new=[data]
    else:
        new = []
    for fname in glob.glob(os.path.join(extract_path, '*.pdf')):

        _, name = os.path.split(fname)
        name, _ = os.path.splitext(name)

        if datetime.strptime(name, '%Y-%m') >= datum:
            newrows = load_PostFinanceExtract(fname)
            new.append(newrows)

    return recfun.stack_arrays(new, autoconvert=True)

