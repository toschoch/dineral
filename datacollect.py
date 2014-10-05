# -- coding: utf-8 --
from subprocess import Popen, PIPE
import numpy as np
import glob, os
from dataload import *
import numpy.lib.recfunctions as recfun
import fnmatch
import locale
from datasave import load_data
from utils import firstOf

__author__ = 'tobi'

confirmation_path = ur'/home/tobi/Finance/Konto Dokumente/Kontos Post/Zahlungsbestätigungen'
extract_path = ur'/home/tobi/Finance/Konto Dokumente/Kontos Post/Konto Auszüge Postkonto'
mastercard_path=ur'/home/tobi/Finance/e-Rechnungen/Mastercard'
visa_path=ur'/home/tobi/Finance/e-Rechnungen/Visa/transaction'
budget_path=ur'/home/tobi/Finance/Budget'
path_on_phone=ur'/mnt/sdcard/expenses'

def load_VisaCardTransactionData(start,stop):
    """ load transaction data from visa card
    """
    files = glob.glob(visa_path+'/*.csv')

    dates=[datetime.strptime(f.split('/')[-1],'%d.%m.%y.csv')   for f in files]
    I = np.argmax(dates).tolist()
    data = load_VisaCardTransaction(files[I])

    I = np.logical_and(data.Datum>=start,data.Datum<=stop)
    data=data[I]

    return data


class ADBException(EnvironmentError):
    def __init__(self,exitcode,strout,strerr):
        self.exitcode,self.strout,self.strerror=exitcode,strout,strerr
    def __str__(self):
        return "error in adb command occured, exitcode {0:d}, output: {1:s}, errors: {2:s}".format(self.exitcode,self.strout,self.strerror)

def load_Expenses_from_phone(start,stop):
    """ load data from phone through adb """

    datafilename='export.csv'

    def call(cmd):
        """
        Execute the external command and get its exitcode, stdout and stderr.
        """

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        proc.wait()
        out, err = proc.communicate()
        exitcode = proc.returncode
        #
        return exitcode, out, err


    # create temporary folder
    tmpdir='.tmpdata'
    os.mkdir(tmpdir)
    os.chdir(tmpdir)
    exitcode, out, err = call(['adb','pull','mnt/sdcard/expenses'])
    if exitcode>0:
        os.chdir('..')
        os.rmdir(tmpdir)
        raise ADBException(exitcode,out,err)

    files_pulled=[e.split('/')[-1] for e in err.splitlines() if e.startswith('pull') and e.find('->')>0]
    # remove files not needed
    for f in files_pulled:
        if f<>datafilename:
            os.remove(f)

    data=load_Expenses(datafilename)

    os.remove(datafilename)
    os.chdir('..')
    os.rmdir(tmpdir)

    I = np.logical_and(data.Datum>=start,data.Datum<=stop)
    data=data[I]

    return data




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


def load_PostFinanceData(start,stop=datetime.now(),data=None,callback=None):
    """ load all data from postfinance account extracts

        Parameters
        ----------
        start:           (datetime.datetime) date from when the data shall be loaded e.g. '01-01-2014'
        stop:            (datetime.datetime)

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    start = firstOf('month',start)

    if data is not None:
        new=[data]
    else:
        new = []

    matches=glob.glob(os.path.join(extract_path, '*.pdf'))

    files2load=[]
    for fname in matches:

        _, name = os.path.split(fname)
        name, _ = os.path.splitext(name)

        month=datetime.strptime(name, '%Y-%m')
        if month>= start and month<=stop:
            files2load.append(fname)

    prog=0
    if len(files2load)>0:
        dprog=100./len(files2load)
    else:
        dprog=0

    for fname in files2load:
        newrows = load_PostFinanceExtract(fname)
        new.append(newrows)
        prog+=dprog
        if callback is not None:
            callback(prog)

    return recfun.stack_arrays(new, autoconvert=True)

def load_MasterCardData(start,stop=datetime.now(),data=None,callback=None):
    """ load all data from mastercard extracts

        Parameters
        ----------
        start:           (datetime.datetime) date from when the data shall be loaded e.g. '01-01-2014'
        stop:            (datetime.datetime)

        Returns
        -------
        (numpy.rec.recarray) table with data, columns: date, description, amount

    """

    start = firstOf('month',start)

    if data is not None:
        new=[data]
    else:
        new = []

    locale.setlocale(locale.LC_TIME,'de_CH.UTF-8')

    files2load = []
    for root, _, filenames in os.walk(mastercard_path):
        for filename in fnmatch.filter(filenames, '*.pdf'):
            fname=os.path.join(root, filename)
            name = '/'.join(fname.split('/')[-2:])
            name, _ = os.path.splitext(name)

            try:
                month=datetime.strptime(name.encode('utf-8'), '%Y/%B')
            except ValueError:
                name=name.split('/')[-1]
                month=datetime.strptime(name.encode('utf-8'),'%Y-%m')

            if month>= start and month<=stop:
                files2load.append(fname)

    prog=0
    if len(files2load)>0:
        dprog=100./len(files2load)
    else:
        dprog=0

    for fname in files2load:

        exceptions = []
        succeeded = False
        for resolution in [200,250,300,320]:
            try:
                newrows = load_MasterCardExtract(fname,resolution) # try with resolution
                succeeded = True
            except Exception as err:
                exceptions.append(err)

        if not succeeded:
            raise exceptions[-1]

        new.append(newrows)
        prog+=dprog
        if callback is not None:
            callback(prog)

    locale.setlocale(locale.LC_TIME,'')

    return recfun.stack_arrays(new, autoconvert=True)

def load_budget(start,stop=datetime.today()):
    """loads a budget file with categories """

    year_from = start.strftime('%y')
    year_to = stop.strftime('%y')

    if year_from == year_to:
        year_from = '{0:02d}'.format(int(year_from)-1)

    fpath = os.path.join(budget_path,year_from+year_to)
    filename =os.path.join(fpath,'Budget.csv')

    return load_data(filename)