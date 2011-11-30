#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

from nimbus.storages.models import StorageGraphicsData
from nimbus.shared import utils
import systeminfo


class Graphics(object):

    def update_db(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        diskinfo = systeminfo.DiskInfo("/")
        total, used, free = diskinfo.get_data()
        new_data = StorageGraphicsData()
        new_data.total = total
        new_data.used = used
        new_data.save()
        # print "Updated Storage: %s of %s" % (used, total)

    def last_days(self, days=7):
        since = datetime.now() - timedelta(days)
        data = StorageGraphicsData.objects.filter(timestamp__gte=since).order_by("-timestamp")
        return data

    def data_to_template(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        data = self.last_days(1)
        timestamps = [item.timestamp.strftime("%H:%M:%S %d/%m/%Y") for item in data]
        values = ['%.1f' % (item.used / 1073741824.0) for item in data]
        if len(data) == 0:
            total = '0.0'
        else:
            total = '%.1f' % (data[len(data) -1].total / 1073741824.0)
        return [{'title': u"Ocupação do disco (GB)",
                'template': 'storage_graph.html',
                'width': "",
                'type': "area",
                'cid_name': "chart_disk_usage",
                'height': "200",
                'lines': {'used': values},
                'total': total,
                'header': timestamps, 'labels': values}]
        