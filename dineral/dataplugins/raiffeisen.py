#!/usr/bin/env python
# encoding: utf-8
"""
postfinance.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals
import logging

log = logging.getLogger(__name__)

import locale
from .abstract import DataPlugin
import subprocess
import re, os, datetime, glob
import pandas as pd
from io import StringIO
import codecs
from builtins import str
import pathlib


class Raiffeisen(DataPlugin):
    """ Load data account extracts from PostFinance """

    TYPE = DataPlugin.DIR

    def load_data(self, period_from, period_to, callback=None):

        start = period_from.year
        end = period_to.year

        new = []
        extracts_path = pathlib.Path(os.path.join(self.properties))
        matches = glob.glob(os.path.join(extracts_path, '*.pdf'))

        log.info('matches: {}'.format(matches))

        locale.setlocale(locale.LC_TIME, 'de_CH.UTF-8')

        files2load = []
        for fname in matches:

            _, name = os.path.split(fname)
            name, _ = os.path.splitext(name)

            year = datetime.datetime.strptime(name, 'Auszug Jahr %Y').date()
            if year.year >= start and year.year <= end:
                files2load.append(fname)
            log.info('checked {}'.format(fname))

        for subdir in extracts_path.iterdir():
            if subdir.is_dir():
                if re.match("[0-9]{4}",subdir.name):
                    year = datetime.datetime.strptime(subdir.name, "%Y").date()
                    if year.year >= start and year.year <= end:
                        p = re.compile(r"(Kontoauszug )?(\w+)( - CH[0-9]+ - [0-9]{4}-[0-9]{2}-[0-9]{2})?.pdf")
                        for fname in subdir.glob("*.pdf"):
                            try:
                                datetime.datetime.strptime(fname.stem, "%B").date()
                                month = fname.stem
                            except:
                                m = p.match(fname.name)
                                if m:
                                    month = m.group(2)
                                else:
                                    continue
                            month = datetime.datetime.strptime("{}-{}".format(year.year,month), "%Y-%B").date()
                            if month >= period_from and month <= period_to:
                                files2load.append(str(fname))


        locale.setlocale(locale.LC_TIME, '')


        prog = 0
        if len(files2load) > 0:
            dprog = 100. / len(files2load)
        else:
            dprog = 0

        if len(files2load) < 1:
            log.warning("No Raiffeisen account extracts found for selected period!")
        else:
            log.info("load files: {}".format(", ".join(files2load)))

        for fname in files2load:
            newrows = self.load_RaiffeisenExtract(fname)
            new.append(newrows)
            prog += dprog
            if callback is not None:
                callback(prog)

        if len(new) > 0:
            data = pd.concat(new, axis=0)
            log.info("loaded {} entries for Raiffeisen extracts".format(len(data)))
        else:
            data = pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)

        return data

    def load_RaiffeisenExtract(self, filename):
        """ loads data from a pdf file and parses the information respect to the format description

            Parameters
            ----------
            filename:           (str) path to file to be loaded

            Returns
            -------
            (pandas DataFrame) table with data columns: date, description, amount

        """
        subprocess.call(['pdftotext', '-layout', filename])

        filename = filename.replace('.pdf', '.txt')

        with codecs.open(filename, 'rb', 'utf-8') as fp:
            lines = fp.readlines()

        starts = [i for i, line in enumerate(lines) if
                  re.match('^\s+Datum\s+Text\s+Belastungen\s+Gutschriften\s+Valuta\s+Saldo\s*$', line)]

        ends = ([starts[0] + 1] + [i for i, line in enumerate(lines) if
                                   re.match('^\s+(Übertrag|Umsatz)\s+[0-9\'.+\s]*$', line)])[1::2]

        data = []
        for s, e in zip(starts, ends):
            page = lines[s + 2:e]
            saldo = float(lines[s + 1].split('  ')[-1].strip('\n +').replace("'", ""))

            s = StringIO(str("".join(page)))

            t = pd.read_table(s, sep='\s{2,}', header=None)
            t.columns = ['Datum', 'Text', 'Betrag', 'Valuta', 'Saldo']
            toadd = t.Datum[pd.isnull(t.Text)]
            t = t[~pd.isnull(t.Text)].copy()

            toadd.index -= 1
            toadd = '\n' + toadd

            t['Text'] = (t.Text + toadd).fillna(t.Text)
            t['Datum'] = pd.to_datetime(t.Datum,dayfirst=True).dt.date
            t['Saldo'] = t.Saldo.str.strip(' +').str.replace("'", "").astype(float)
            t['Betrag'] = t.Betrag.str.strip(' +').str.replace("'", "").astype(float)
            t['Betrag'] = t.Saldo.diff().fillna(t.Saldo - saldo)
            data.append(t)
        data = pd.concat(data).reset_index(drop=True).drop(['Saldo','Valuta'],axis=1).rename(columns={'Betrag':'Lastschrift'})

        data['Kategorie'] = self.NOCATEGORY
        data['Lastschrift'] *= -1

        return data
