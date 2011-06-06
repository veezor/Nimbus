#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import cPickle as pickle
from threading import Lock
from contextlib import nested
from urllib2 import URLError

from django.conf import settings

import systeminfo
from nimbus.offsite.models import Offsite


def _sort_key_function(date):
    day, month, year = date
    return (year, month, day)


class GraphDataManager(object):
    """ data = {'data' :
                    {
                  '<date>' : {
                    'offsite' : number,
                    'disk' : number
                   }
              },
            'last_update' : <datetime>
         } """
    MAX_DAYS = 7

    def __init__(self):
        self.filename = settings.NIMBUS_GRAPHDATA_FILENAME
        self.lock = Lock()
        self.data = None
        self.open()
        #self.update()

    def open(self):
        try:
            with nested(file(self.filename),self.lock) as (fileobj, lock):
                self.data = pickle.load(fileobj)
        except IOError, error:
            now = datetime.datetime.now()
            last_update = now - datetime.timedelta(seconds=600)
            self.data = {"data" : {},
                         "last_update" : last_update}

    def save(self, data):
        with nested(file(self.filename, "w"),self.lock) as (fileobj, lock):
            pickle.dump(data, fileobj)

    def get_offsite_data(self):
        s3 = Offsite.get_s3_interface()
        if offsite.active:
            try:
                return s3.get_usage()
            except URLError, error:
                return 0.0
        else:
            return 0.0

    def get_disk_data(self):
        try:
            diskinfo = systeminfo.DiskInfo("/bacula")
            diskusage = diskinfo.get_used()
            return diskusage
        except OSError, error:
            return 0.0

    def _list_measures(self, datatype):
        data = self.data['data']
        measures = []
        for date in sorted(data, key=_sort_key_function):
            fmt_date = "/".join([str(x) for x in date])
            value = data[date][datatype]
            measures.append((fmt_date, value))
        return measures

#    def _list_days(self):
#        now = datetime.datetime.now()
#        days = []
#
#        for i in xrange(self.MAX_DAYS - 1,0,-1):
#            diff = datetime.timedelta(days=i)
#            days.append( now - diff )
#
#        days.append(now)
#
#        return [ d.strftime("%d/%m/%y") for d in days ]

    def list_disk_measures(self):
        return self._list_measures('disk')

    def list_offsite_measures(self):
        return self._list_measures('offsite')

    def update(self):
        data = self.data['data']
        last_update = self.data['last_update']
        now = datetime.datetime.now()
        diff = now - last_update
        five_minutes = datetime.timedelta(minutes=5)
        if diff < five_minutes:
            return
        data_key = (now.day, now.month, now.year)
        if data_key in data:
            offsite_value = data[data_key]['offsite'] # preserve old measeure on errors
        else:
            offsite_value = 0.0
            data[data_key] = {}
        data[data_key]['disk'] = self.get_disk_data()
        data[data_key]['offsite'] = self.get_offsite_data() or offsite_value
        self.data['last_update'] = now
        self._remove_old_entries()
        self.save(self.data)

    def _remove_old_entries(self):
        with self.lock:
            data = self.data['data']
            days = sorted(data, key=_sort_key_function)
            num_days = len(days)
            if num_days > self.MAX_DAYS:
                extra = days[:-self.MAX_DAYS]
                for day in extra:
                    del data[day]
