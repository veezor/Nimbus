#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.schedules.views',
                        (r'^add/$', 'add_schedule'),
                        (r'^test/$', 'test'),
                        (r'^(?P<object_id>\d+)/edit/$', 'edit'),
                        (r'^delete/(?P<schedule_id>\d+)$', 'delete'),
)
