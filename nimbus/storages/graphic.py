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
        print result
        return result

    def data_to_template(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        diskinfo = systeminfo.DiskInfo("/bacula")
        t, u, f = diskinfo.get_data()
        used = u / 1073741824.0
        total = t / 1073741824.0
        r = [{'title': u"Ocupação do disco: %.1f de %.1fGB (%.1f%%)" %(used, total, 100*used/total),
                'template': 'storage_graph.html',
                'cid_name': "chart_disk_usage",
                'height': "200",
                'total': total,
                'upper_limit': int(total*1.3)}]
        return r