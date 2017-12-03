#!/usr/bin/env python
# encoding: utf-8
"""
mastercard.py

Created by Tobias Schoch on 02.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals

from .abstract import DataPlugin

import os, codecs, locale, fnmatch
from datetime import datetime
import pandas as pd
from .utils import firstOf, TemporaryDirectory

import pkg_resources
import subprocess

import logging
import re
from builtins import str

log = logging.getLogger(__name__)


class MasterCard(DataPlugin):
    """ Load data MasterCard Credit Card Account Extracts """

    TYPE = DataPlugin.DIR

    def load_data(self, period_from, period_to, callback=None):
        """ load all data from mastercard extracts

            Parameters
            ----------
            start:           (datetime.datetime) date from when the data shall be loaded e.g. '01-01-2014'
            stop:            (datetime.datetime)

            Returns
            -------
            (numpy.rec.recarray) table with data, columns: date, description, amount

        """

        start = firstOf('month', period_from)
        stop = period_to

        new = []

        locale.setlocale(locale.LC_TIME, 'de_CH.UTF-8')

        files2load = []
        for root, _, filenames in os.walk(self.properties):
            for filename in fnmatch.filter(filenames, '*.pdf'):
                fname = os.path.join(root, filename)
                name = '/'.join(fname.split('/')[-2:])
                name, _ = os.path.splitext(name)
                name = name.encode('utf-8')
                try:
                    month = datetime.strptime(name, '%Y/%B').date()
                except ValueError:
                    name = name.split('/')[-1]
                    month = datetime.strptime(name, '%Y-%m').date()

                if month >= start and month <= stop:
                    files2load.append(fname)

        resolutions = [400,500,600]

        prog = 0
        if len(files2load) > 0:
            dprog = 100. / (len(files2load) * len(resolutions))
        else:
            dprog = 0

        if len(files2load) > 0:
            log.info("load files: {}".format(", ".join(files2load)))
        else:
            log.warn("No MasterCard account extracts found for selected period!")

        for fname in files2load:

            exceptions = []
            succeeded = False

            newrows = self.load_MasterCardExtract_without_ocr(fname)

            # for resolution in resolutions:
            #     try:
            #         newrows = self.load_MasterCardExtract(fname, resolution)  # try with resolution
            #         succeeded = True
            #         break
            #     except Exception as err:
            #         exceptions.append(err)
            #     prog += dprog
            #     if callback is not None:
            #         callback(prog)

            # if not succeeded:
            #     raise exceptions[-1]

            new.append(newrows)

        locale.setlocale(locale.LC_TIME, '')

        if len(new) > 0:
            return pd.concat(new, axis=0)
        else:
            return pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)

    def load_MasterCardExtract_without_ocr(self, filename):
        """
        load data from a pdf file
        Args:
            filename: (str) path to file to be loaded

        Returns:
            (pandas.Dataframe) table with transaction data
        """
        # create temporary directory, with cleanup
        with TemporaryDirectory() as tmp:

            # local filename
            _, target = os.path.split(filename)
            target = os.path.join(tmp,target.replace('.pdf', '.txt'))

            subprocess.call(['pdftotext', '-layout', filename, target], cwd=tmp)


            with codecs.open(target, 'rb', 'utf-8') as fp:

                lines = fp.read().splitlines()

        lines = map(str, lines)


        newentry = re.compile("([0-9]{2,2}.[0-9]{2,2}.[0-9]{2,2}) ([\D\s-]+) ([A-Z]{3,3} [0-9]+.[0-9]{2,2})? \W* ([0-9]+.[0-9]{2,2})[\s0-9.]*",re.UNICODE)

        table = []
        it = iter(lines)

        try:
            while True:

                line = next(it)

                line = line.strip()
                m = newentry.match(line)
                while not m:
                    line = next(it).strip()
                    m = newentry.match(line)

                date = m.group(1)
                text = m.group(2).strip()
                if m.group(3):
                    text += ' ' + m.group(3).strip()
                amount = m.group(4)

                line = next(it).strip()

                while line!='':
                    text += '\n'+line
                    line = next(it).strip()

                if text.lower().startswith('saldovortrag'): continue
                if text.lower().startswith('ihre esr-zahlung'): continue

                table.append([date,text,amount])




        except StopIteration:
            pass

        # convert types
        rec = pd.DataFrame(table, columns=['Datum', 'Text', 'Lastschrift'])
        rec['Datum'] = rec['Datum'].apply(lambda s: datetime.strptime(s, '%d.%m.%y'))
        rec.Datum = pd.DatetimeIndex(rec.Datum).date
        rec['Lastschrift'] = rec['Lastschrift'].astype(float)

        rec['Kategorie'] = self.NOCATEGORY

        return rec


    def load_MasterCardExtract(self, filename, resolution):
        """ loads data from a pdf file and parses the information respect to the format description

            Parameters
            ----------
            filename:           (str) path to file to be loaded
            resolution:         (int) resolution dpi for converting the pdf to png

            Returns
            -------
            (numpy.rec.recarray) table with data, columns: date, description, amount

        """

        column_headers = ['Datum', 'Text', 'Belastungen', 'Gutschriften', 'Datum']
        align = [0, 0, 1, 1, 1, 2]

        # find bash script
        pdf2text = pkg_resources.resource_filename('dineral','/bash/SecuredPDF2txt.sh')

        # create temporary directory, with cleanup
        with TemporaryDirectory() as tmp:

            # local filename
            _, target = os.path.split(filename)

            # parse pdf to text
            subprocess.call([pdf2text,filename.encode('utf-8'), target.encode('utf-8'),str(resolution)], cwd=tmp)
            #os.system('../bash/SecuredPDF2txt.sh ' + filename.encode('utf-8') + ' ' + str(resolution))
            target = os.path.join(tmp,target.replace('.pdf', '.txt'))


            with codecs.open(target, 'r', 'utf-8') as fp:
                lines = fp.read().splitlines()


        table = []

        it = iter(lines)

        try:
            while True:

                line = next(it)

                # search for column headers
                col_index = [line.find(col) for col in column_headers]

                # if column headers found -> store indices
                if min(col_index) >= 0:

                    line = next(it)
                    line = next(it)

                    # while no new page started, first character not space
                    while line.find('UEBERTRAG AUF NAECHSTE SEITE') < 0 or line.find('Saldo zu unseren Gunsten') < 0:

                        # try to parse date
                        try:
                            date = line.split(' ')[0]
                            date = datetime.strptime(date, "%d.%m.%y")

                        except (IndexError, ValueError):
                            line = next(it)
                            continue

                        # except saldovortrag and ESR-ZAHLUNG
                        if line.find('SALDOVORTRAG') >= 0 or line.replace(' ','').find('ESR-ZAHLUNG') >= 0 :
                            line = next(it)
                            continue

                        text = [u' '.join(line.split(' ')[1:-2])]
                        f_str = line.split(' ')[-2]
                        amount = float(f_str.replace("'", ""))

                        # try to parse date
                        while True:
                            line = next(it)
                            try:
                                d = line.split(' ')[0]
                                d = datetime.strptime(d, "%d.%m.%y")

                                table.append([date, str(u'\n'.join(text)), amount])

                                break

                            except (IndexError, ValueError):
                                if line == '': continue
                                if (line.find('UEBERTRAG AUF NAECHSTE SEITE') >= 0) \
                                    or (line.find('Saldo zu unseren Gunsten') >= 0) \
                                    or (line.find('Kartentotal')>=0):
                                    table.append([date, '\n'.join(text), amount])
                                    break
                                text.append(line)

        except StopIteration:
            pass

        # crop and convert types
        headers = ['Datum', 'Text', 'Lastschrift']
        rec = pd.DataFrame(table, columns=headers)
        rec.Datum = pd.DatetimeIndex(rec.Datum).date

        rec['Kategorie'] = self.NOCATEGORY

        return rec
