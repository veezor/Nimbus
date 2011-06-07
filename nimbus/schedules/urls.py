#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.schedules.views',
                        (r'^add/$', 'add_schedule'),
                        (r'^(?P<object_id>\d+)/edit/$', 'edit'),
)
