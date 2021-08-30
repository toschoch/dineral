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
from datetime import datetime, date
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
                #name = name.encode('utf-8')
                try:
                    month = datetime.strptime(name, '%Y/%B').date()
                except ValueError:
                    name = name.split('/')[-1]
                    month = datetime.strptime(name, '%Y-%m').date()

                if month >= start and month <= stop:
                    files2load.append((fname, month))

        if len(files2load) > 0:
            log.info("load files: {}".format(", ".join([f for f, _ in files2load])))
        else:
            log.warning("No MasterCard account extracts found for selected period!")

        for fname, month in files2load:

            if month >= date(2019, 4, 1):
                newrows = self.load_MasterCardExtract_2019(fname)
            else:
                newrows = self.load_MasterCardExtract_without_ocr(fname)

            new.append(newrows)

        locale.setlocale(locale.LC_TIME, '')

        if len(new) > 0:
            return pd.concat(new, axis=0)
        else:
            return pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)


    def load_MasterCardExtract_2019(self, filename):
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
            target = os.path.join(tmp, target.replace('.pdf', '.txt'))

            subprocess.call(['pdftotext', '-layout', filename, target], cwd=tmp)

            with codecs.open(target, 'rb', 'utf-8') as fp:
                lines = fp.read().splitlines()

        lines = map(str, lines)

        newentry = re.compile(
            "([0-9]{2,2}.[0-9]{2,2}.[0-9]{2,2}) {1,}([0-9]{2,2}.[0-9]{2,2}.[0-9]{2,2}) {1,}(.+) {2,}([A-Z]{3,3} +[0-9']+.[0-9]{2,2})? {2,}([+-]?[0-9']+.[0-9]{2,2})$",
            re.UNICODE)

        table = []
        it = iter(lines)

        try:
            line = next(it)

            while True:

                m = newentry.match(line)
                while not m:
                    line = next(it).strip()
                    m = newentry.match(line)

                date = m.group(1)
                text = m.group(3).strip()
                if m.group(4):
                    text += ' ' + m.group(4).strip()
                amount = m.group(5).replace("'","")

                text = re.sub(' {2,}', ' ', text)

                line = next(it).strip()

                while line != '' and not newentry.match(line):
                    text += '\n' + re.sub(' {2,}', ' ', line)
                    line = next(it).strip()

                table.append([date, text, amount])

        except StopIteration:
            pass

        # convert types
        rec = pd.DataFrame(table, columns=['Datum', 'Text', 'Lastschrift'])
        rec['Datum'] = rec['Datum'].apply(lambda s: datetime.strptime(s, '%d.%m.%y'))
        rec.Datum = pd.DatetimeIndex(rec.Datum).date
        rec['Lastschrift'] = rec['Lastschrift'].astype(float)

        rec['Kategorie'] = self.NOCATEGORY

        return rec


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


        newentry = re.compile(r"([0-9]{2,2}.[0-9]{2,2}.[0-9]{2,2}) (.+?(?= {2,2})) ([A-Z]{3,3} [0-9]+.[0-9]{2,2})? \W* ([0-9]+.[0-9]{2,2})[\s0-9.]*",re.UNICODE)

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