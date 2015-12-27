#!/usr/bin/env python
# encoding: utf-8
"""
mastercard.py

Created by Tobias Schoch on 02.12.15.
Copyright (c) 2015. All rights reserved.
"""
# from __future__ import unicode_literals

from abstract import DataPlugin

import os, codecs, locale, fnmatch
from datetime import datetime
import pandas as pd
from utils import firstOf
import logging

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

        start = firstOf('month',period_from)
        stop = period_to


        new = []

        locale.setlocale(locale.LC_TIME,'de_CH.UTF-8')

        files2load = []
        for root, _, filenames in os.walk(self.properties):
            for filename in fnmatch.filter(filenames, '*.pdf'):
                fname=os.path.join(root, filename)
                name = '/'.join(fname.split('/')[-2:])
                name, _ = os.path.splitext(name)

                try:
                    month=datetime.strptime(name.encode('utf-8'), '%Y/%B').date()
                except ValueError:
                    name=name.split('/')[-1]
                    month=datetime.strptime(name.encode('utf-8'),'%Y-%m').date()

                if month>= start and month<=stop:
                    files2load.append(fname)

        resolutions = [200,250,300,320]

        prog=0
        if len(files2load)>0:
            dprog=100./(len(files2load)*len(resolutions))
        else:
            dprog=0

        log.info("load files: {}".format(", ".join(files2load)))

        for fname in files2load:

            exceptions = []
            succeeded = False
            for resolution in resolutions:
                try:
                    newrows = self.load_MasterCardExtract(fname,resolution) # try with resolution
                    succeeded = True
                except Exception as err:
                    exceptions.append(err)
                prog+=dprog
                if callback is not None:
                    callback(prog)

            if not succeeded:
                raise exceptions[-1]

            new.append(newrows)


        locale.setlocale(locale.LC_TIME,'')

        if len(new)>0:
            return pd.concat(new,axis=0)
        else:
            return pd.DataFrame(columns=self.DEFAULTDATACOLUMNS)

    def load_MasterCardExtract(self,filename,resolution):
        """ loads data from a pdf file and parses the information respect to the format description

            Parameters
            ----------
            filename:           (str) path to file to be loaded
            resolution:         (int) resolution dpi for converting the pdf to png

            Returns
            -------
            (numpy.rec.recarray) table with data, columns: date, description, amount

        """

        # parse pdf to text
        os.system('./SecuredPDF2txt.sh '+filename.encode('utf-8')+' '+str(resolution))
        filename=filename.replace('.pdf','.txt')

        column_headers=['Datum','Text','Belastungen','Gutschriften','Datum']
        align=[0,0,1,1,1,2]

        with codecs.open(filename,'r','utf-8') as fp:
            lines = fp.read().splitlines()

        # remove the text file
        os.remove(filename)

        table=[]

        it = iter(lines)

        try:
            while True:

                line = it.next()

                # search for column headers
                col_index = [line.find(col) for col in column_headers]

                # if column headers found -> store indices
                if min(col_index)>=0:

                    line = it.next()
                    line = it.next()


                    # while no new page started, first character not space
                    while line.find('UEBERTRAG AUF NAECHSTE SEITE')<0 or line.find('Saldo zu unseren Gunsten')<0:

                        # try to parse date
                        try:
                            date=line.split(' ')[0]
                            date=datetime.strptime(date,"%d.%m.%y")

                        except (IndexError,ValueError):
                            line = it.next()
                            continue

                        # except saldovortrag and ESR-ZAHLUNG
                        if line.find('SALDOVORTRAG')>=0 or line.find('IHRE ESR-ZAHLUNG')>=0:
                            line = it.next()
                            continue

                        text=[u' '.join(line.split(' ')[1:-2])]
                        f_str = line.split(' ')[-2]
                        amount=float(f_str.replace("'",""))

                        # try to parse date
                        while True:
                            line = it.next()
                            try:
                                d=line.split(' ')[0]
                                d=datetime.strptime(d,"%d.%m.%y")

                                table.append([date,unicode(u'\n'.join(text)),amount])

                                break

                            except (IndexError,ValueError):
                                if line=='':continue
                                if line.find('UEBERTRAG AUF NAECHSTE SEITE')>=0 or line.find('Saldo zu unseren Gunsten')>=0:
                                    table.append([date,'\n'.join(text),amount])
                                    break
                                text.append(line)

        except StopIteration:
            pass

        # crop and convert types
        headers=['Datum','Text','Lastschrift']
        rec=pd.DataFrame(table,columns=headers)
        rec.Datum = pd.DatetimeIndex(rec.Datum).date

        rec['Kategorie']=self.NOCATEGORY

        return rec
