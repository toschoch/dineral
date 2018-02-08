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
                if re.match("[0-9]{4}",subdir.name):
                    year = datetime.datetime.strptime(subdir.name, "%Y").date()
                    if year.year >= start and year.year <= end:
                        p = re.compile(r"(Kontoauszug )?(\w+)( [0-9]{4} - CH[0-9]+ - [0-9]{4}-[0-9]{2}-[0-9]{2})?.pdf")
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

        if len(files2load)<1:
            for fname in extracts_path.iterdir():
                if fname.is_file():
                    if re.match('Auszug Jahr [0-9]{4}',fname.stem):
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
        subprocess.call(['pdftotext', '-layout', filename])

        filename = filename.replace('.pdf', '.txt')

        with codecs.open(filename, 'rb', 'utf-8') as fp:
            lines = fp.readlines()

        starts = [i for i, line in enumerate(lines) if
                  re.match('^\s+Datum\s+Text\s+Belastungen\s+Gutschriften\s+Valuta\s+Saldo\s*$', line)]

        ends = ([starts[0] + 1] + [i for i, line in enumerate(lines) if
                                   re.match('^\s+(Übertrag|Umsatz)\s+[0-9\'.+\s]*$', line)])[1::2]

        data = []
        colspecs = None
        for s, e in zip(starts, ends):
            page = lines[s + 2:e]
            saldo = float(lines[s + 1].split('  ')[-1].strip('\n +').replace("'", ""))

            if len(page)<1:
                continue

            s = StringIO(str("".join(page)))

            if colspecs is None:
                fwr = FixedWidthReader(s,colspecs='infer', delimiter=' ',comment='#')
                colspecs = fwr.colspecs
                s = StringIO(str("".join(page)))

            t = pd.read_fwf(s, header=None, colspecs=colspecs)
            data.append(t)
        t = pd.concat(data,axis=0).reset_index(drop=True)
        cols = t.columns.tolist()
        tomerge = len(cols)-6
        text = t.iloc[:, 1:1 + tomerge].fillna("").astype(str).apply(" ".join,axis=1)
        t = t.drop(labels=list(range(1,1+tomerge)),axis=1)
        t.columns = ['Datum', 'Belastungen', 'Gutschriften', 'Valuta', 'Saldo',
                   'Sign']  # ''Text', 'Betrag', 'Valuta', 'Saldo']
        t['Text'] = text

        toadd = t.Text.iloc[:-1].groupby((~pd.isnull(t.Datum)).cumsum()).agg("\n".join).reset_index(drop=True)
        t = t[~pd.isnull(t.Datum)].copy().reset_index(drop=True)
        t['Text'] = toadd

        t['Datum'] = pd.to_datetime(t.Datum,dayfirst=True).dt.date
        t['Valuta'] = pd.to_datetime(t.Valuta,dayfirst=True).dt.date
        t['Saldo'] = t.Saldo.str.strip(' +').str.replace("'", "").astype(float)
        t = t.rename(columns={'Gutschriften':'Betrag'})
        t['Betrag'] = t.Betrag.str.replace("'", "").astype(float)
        t['Belastungen'] = -t.Belastungen.str.replace("'", "").astype(float)
        t['Betrag'] = t['Betrag'].fillna(t.Belastungen)
        #t['Betrag'] = t.Saldo.diff().fillna(t.Saldo - saldo)
        data = t.drop(['Saldo','Valuta','Belastungen','Sign'],axis=1).rename(columns={'Betrag':'Lastschrift'})

        data['Kategorie'] = self.NOCATEGORY
        data['Lastschrift'] *= -1

        return data
