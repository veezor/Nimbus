#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db.models import Max, Min
from urllib2 import URLError
from datetime import datetime, timedelta

from nimbus.offsite.models import Offsite, OffsiteGraphicsData
from nimbus.offsite.S3 import S3AuthError


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
                now_used = s3.get_size()
            except (URLError, S3AuthError), error:
                now_used = 0.0
            new_data = OffsiteGraphicsData()
            new_data.total = plan_total
            new_data.used = now_used
            new_data.save()


    def last_days(self, days=90):
        since = datetime.now() - timedelta(days)
        data = OffsiteGraphicsData.objects.filter(timestamp__gte=since).order_by("-timestamp")
        return data
        

    # def unify_days(self, data):
    #     result = []
    #     days = [item.timestamp.date() for item in data]
    #     days = list(set(days))
    #     days.reverse()
    #     for day in days:
    #         day_data = OffsiteGraphicsData.objects.filter(timestamp__year=day.year,
    #                     timestamp__month=day.month, timestamp__day=day.day, )\
    #                     .aggregate(Max('used'), Min('used'), Max('total'))
    #         result.append([day.strftime("%d/%m/%Y"),
    #                        day_data['used__max'],
    #                        day_data['used__min'],
    #                        day_data['total__max']])
    #     return result

        
    def data_to_template(self):
        """Metodo obrigatorio para todas as classes Graphics"""
        if self.offsite_if_active():
            if OffsiteGraphicsData.objects.count():
                most_recent = OffsiteGraphicsData.objects.order_by("-timestamp")[0]
                total_GB = most_recent.total / 1073741824.0
                used_GB = most_recent.used / 1073741824.0
                total = most_recent.total
                percent_used = 100.0*used_GB/total_GB
            else:
                total_GB, used_GB, total, percent_used = 0.0, 0.0, 0.0, 0.0
            return [{'title': u"Ocupação do disco:",
                    'used': used_GB,
                    'percent_used': percent_used,
                    'warn_level': 85.0, # percent
                    'template': 'offsite_graph.html',
                    'width': "",
                    'cid_name': "chart_offsite_usage",
                    'height': "200",
                    'total': total,
                    'total_GB': total_GB,
                    'upper_limit': int(total_GB * 1.3)}]
        else:
            return []
