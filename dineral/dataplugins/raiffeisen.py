#!/usr/bin/env python
# encoding: utf-8
"""
postfinance.py

Created by Tobias Schoch on 03.12.15.
Copyright (c) 2015. All rights reserved.
"""
from __future__ import unicode_literals
import logging
from tempfile import TemporaryDirectory

log = logging.getLogger(__name__)

import locale
from pandas.io.parsers import FixedWidthReader
from .abstract import DataPlugin
import subprocess
import re, os, datetime, glob
import pandas as pd
from io import StringIO
import numpy as np
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

        for subdir in extracts_path.iterdir():
            if subdir.is_dir():
                if re.match("[0-9]{4}", subdir.name):
                    year = datetime.datetime.strptime(subdir.name, "%Y").date()
                    if year.year >= start and year.year <= end:
                        p = re.compile(r"(Kontoauszug )?(\w+)( [0-9]{4} - CH[0-9]+ - [0-9]{4}-[0-9]{2}-[0-9]{2})?.pdf")
                        p2 = re.compile(
                            r"(Kontoauszug )([0-9]{2}.[0-9]{2}.[0-9]{4}) - ([0-9]{2}.[0-9]{2}.[0-9]{4}) - CH[0-9]+ - [0-9]{4}-[0-9]{2}-[0-9]{2}.pdf")
                        for fname in subdir.glob("*.pdf"):
                            try:
                                datetime.datetime.strptime(fname.stem, "%B").date()
                                month = fname.stem
                            except:
                                m = p.match(fname.name)
                                if m:
                                    month = m.group(2)
                                    month = datetime.datetime.strptime("{}-{}".format(year.year, month), "%Y-%B").date()
                                else:
                                    m = p2.match(fname.name)
                                    if m:
                                        month = m.group(2)
                                        month = datetime.datetime.strptime(month, "%d.%m.%Y").date()
                                    else:
                                        continue
                            if month >= period_from and month <= period_to:
                                files2load.append(str(fname))

        if len(files2load) < 1:
            for fname in extracts_path.iterdir():
                if fname.is_file():
                    if re.match('Auszug Jahr [0-9]{4}', fname.stem):
                        year = datetime.datetime.strptime(fname.stem, 'Auszug Jahr %Y').date()
                        if year.year >= start and year.year <= end:
                            files2load.append(fname)
                        log.info('checked {}'.format(fname))

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

        # create temporary directory, with cleanup
        with TemporaryDirectory() as tmp:

            _, fname = os.path.split(filename)
            txtfile = os.path.join(tmp, fname.replace('.pdf', '.txt'))

            subprocess.call(['pdftotext', '-layout', filename, txtfile], cwd=tmp)

            with codecs.open(txtfile, 'rb', 'utf-8') as fp:
                lines = fp.readlines()

        starts = []
        for i, line in enumerate(lines):
            m = re.match(r'^\s+(Datum)\s+(Text)\s+(Belastungen)\s+(Gutschriften)\s+(Valuta\s+)?(Saldo)\s*$', line)
            if m:
                starts.append((i, m))

        ends = ([starts[0][0] + 1] + [i for i, line in enumerate(lines) if
                                      re.match(r'^\s+(Übertrag|Umsatz)\s+[0-9\'.+\s]*$', line)])[1::2]

        data = []
        colspecs = None
        for s, e in zip(starts, ends):
            page = lines[s[0] + 2:e]
            has_valuta = s[1].group(5) is not None

            if len(page) < 1:
                continue

            entries = []
            for i, line in enumerate(page):
                if has_valuta:
                    m = re.match(r'^\s+([0-9]{2}\.[0-9]{2}\.[0-9]{2})\s+(.+)\s{2,}([0-9\'.]+)\s+([0-9]{2}\.[0-9]{2}\.[0-9]{2})\s+([0-9\'.]+)$', line)
                else:
                    m = re.match(r'^\s+([0-9]{2}\.[0-9]{2}\.[0-9]{2})\s+(.+)\s{2,}([0-9\'.]+)\s+([0-9\'.]+)$', line)
                if m:
                    entries.append((i, m))

            n = len(entries)
            for i, entry in enumerate(entries):
                j, m = entry
                k = None
                if i < (n-1):
                    k = entries[i + 1][0]

                text = "\n".join([m.group(2).strip()] + [pline.strip() for pline in page[j + 1:k] if pline.strip() != ""])

                belastung, gutschrift = np.NAN, np.NAN
                if m.start(3) < s[1].start(4):
                    belastung = float(m.group(3).replace("'", ""))
                else:
                    gutschrift = float(m.group(3).replace("'", ""))

                valuta = pd.NaT
                saldo = np.NAN
                if has_valuta:
                    saldo = float(m.group(5).replace("'", ""))
                    if m.group(4) is not None:
                        valuta = pd.to_datetime(m.group(4))
                else:
                    saldo = float(m.group(4).replace("'", ""))

                t = [pd.to_datetime(m.group(1), dayfirst=True, yearfirst=False), text, belastung, gutschrift, valuta, saldo]
                data.append(t)
        t = pd.DataFrame(data)
        t.columns = ['Datum', 'Text', 'Belastungen', 'Gutschriften', 'Valuta', 'Saldo']

        t = t.rename(columns={'Gutschriften': 'Betrag'})
        t['Belastungen'] = -t.Belastungen
        t['Betrag'] = t['Betrag'].fillna(t.Belastungen)
        data = t.drop(['Saldo', 'Belastungen', 'Valuta'], axis=1).rename(columns={'Betrag': 'Lastschrift'})

        data['Kategorie'] = self.NOCATEGORY
        data['Lastschrift'] *= -1

        return data
