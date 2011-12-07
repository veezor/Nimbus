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
            # print "Updated Offsite: %s of %s" % (now_used, plan_total)

    def last_days(self, days):
        since = datetime.now() - timedelta(days)
        data = OffsiteGraphicsData.objects.filter(timestamp__gte=since).order_by("-timestamp")
        return data
        

    def unify_days(self, data):
        result = []
        days = [item.timestamp.date() for item in data]
        days = list(set(days))
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
        if self.offsite_if_active():
            days = self.last_days(1)
            data = self.unify_days(days)
            timestamps = []
            max_values = []
            min_values = []
            total = 0.0
            for day, umax, umin, t in data:
                timestamps.append(day)
                max_values.append(umax)
                min_values.append(umin)
                total = t / 1073741824.0
            return [{'title': u"Ocupação do espaço Offsite (GB)",
                    'template': 'offsite_graph.html',
                    'width': "",
                    'type': "area",
                    'cid_name': "chart_offsite_usage",
                    'height': "200",
                    'lines': {'used': max_values, 'min_used': min_values},
                    'total': total,
                    'header': timestamps, 'labels': max_values}]
        else:
            return []