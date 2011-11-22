#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from urllib2 import URLError
from datetime import datetime, timedelta

from nimbus.offsite.models import Offsite, OffsiteGraphicsData


class Graphics(object):

    def offsite_if_active(self):
        offsite = Offsite.get_instance()
        if offsite.active:
            return offsite

    def update_db(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        offsite = self.offsite_if_active()
        if offsite:
            plan_total = offsite.plan_size
            try:
                s3 = Offsite.get_s3_interface()
                now_used = s3.get_usage()
            except URLError, error:
                now_used = 0.0
            # now_used = 1000
            new_data = OffsiteGraphicsData()
            new_data.total = plan_total
            new_data.used = now_used
            new_data.save()
            print "Updated Offsite: %s of %s" % (now_used, plan_total)

    def last_days(self, days):
        since = datetime.now() - timedelta(days)
        data = OffsiteGraphicsData.objects.filter(timestamp__gte=since).order_by("-timestamp")
        return data
        
    def data_to_template(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        data = self.last_days(1)
        timestamps = [item.timestamp.strftime("%H:%M:%S %d/%m/%Y") for item in data]
        values = ['%.1f' % (item.used) for item in data]
        total = '%.1f' % (data[len(data) -1].total)
        return [{'title': u"Ocupação do espaço Offsite (GB)",
                'template': 'offsite_graph.html',
                'width': "",
                'type': "area",
                'cid_name': "chart_offsite_usage",
                'height': "200",
                'lines': {'used': values},
                'total': total,
                'header': timestamps, 'labels': values}]    