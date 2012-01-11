#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

from django.db.models import Max, Min
from nimbus.storages.models import StorageGraphicsData
from nimbus.shared import utils
import systeminfo


class Graphics(object):

    def update_db(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        diskinfo = systeminfo.DiskInfo("/bacula")
        total, used, free = diskinfo.get_data()
        new_data = StorageGraphicsData()
        new_data.total = total
        new_data.used = used
        new_data.save()
        # print "Updated Storage: %s of %s" % (used, total)

    def last_days(self, days=14):
        since = datetime.now() - timedelta(days)
        data = StorageGraphicsData.objects.filter(timestamp__gte=since).order_by("-timestamp")
        return data

    def unify_days(self, data):
        result = []
        days = [item.timestamp.date() for item in data]
        days = list(set(days))
        days.reverse()
        for day in days:
            day_data = StorageGraphicsData.objects.filter(timestamp__year=day.year,
                        timestamp__month=day.month, timestamp__day=day.day, )\
                        .aggregate(Max('used'), Min('used'), Max('total'))
            result.append([day.strftime("%d/%m/%Y"),
                           day_data['used__max'],
                           day_data['used__min'],
                           day_data['total__max']])
        return result

    def data_to_template(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        days = self.last_days(1)
        data = self.unify_days(days)
        timestamps = []
        max_values = []
        min_values = []
        total = 0.0
        for day, umax, umin, t in data:
            timestamps.append(day)
            max_values.append(umax / 1073741824.0)
            min_values.append(umin / 1073741824.0)
        diskinfo = systeminfo.DiskInfo("/bacula")
        t, u, f = diskinfo.get_data()
        total = t / 1073741824.0
        timestamps.append("Agora")
        max_values.append(u / 1073741824.0)
        return [{'title': u"Ocupação do disco (GB)",
                'template': 'storage_graph.html',
                'width': "",
                'type': "area",
                'cid_name': "chart_disk_usage",
                'height': "200",
                'lines': {'used': max_values},# 'min_used': min_values},
                'total': total,
                'header': timestamps, 'labels': max_values}]
        