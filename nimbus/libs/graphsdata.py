#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
import cPickle as pickle
from threading import Lock
from contextlib import nested
from urllib2 import URLError

from django.conf import settings

import systeminfo

def _sort_key_function(date):
    day, month, year = date
    return (year, month, day)


class GraphDataManager(object):
    """ data = {'data' :
                    {
                  '<date>' : {
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
        try:
            for date in sorted(data, key=_sort_key_function):
                fmt_date = "/".join([str(x) for x in date])
                value = data[date][datatype]
                measures.append((fmt_date, value))
        except KeyError:
            pass
        
        self._complete_measures(measures)
        return measures


    def _complete_measures(self, measures):
        if len(measures) > 1:
            day = measures[0][0] # first (date, value)
            day = datetime.datetime.strptime(day + " 00:00", "%d/%m/%Y %H:%M")
        else:
            day = datetime.datetime.now()

        needs =  self.MAX_DAYS - len(measures)
        for d in xrange(1, needs + 1):
            diff = datetime.timedelta(days=d)
            old_day = day - diff
            old_day_str = "%d/%d/%d" % (old_day.day, old_day.month, old_day.year)
            measures.insert(0, (old_day_str, 0))


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


    def update(self):
        data = self.data['data']
        last_update = self.data['last_update']
        now = datetime.datetime.now()
        diff = now - last_update
        five_minutes = datetime.timedelta(minutes=5)
        if diff < five_minutes:
            return
        data_key = (now.day, now.month, now.year)
        
        if not data_key in data:
            data[data_key] = {}

        old_offsite_value = 0

        data[data_key]['disk'] = self.get_disk_data()

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



def update_disk_graph():
    data_manager = GraphDataManager()
    data_manager.update()
