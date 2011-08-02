#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.schedules.views',
                        (r'^add/$', 'add'),
                        (r'^do_add/$', 'do_add'),
                        (r'^do_edit/$', 'do_edit'),
                        # (r'^test/$', 'test'),
                        (r'^(?P<object_id>\d+)/edit/$', 'edit'),
                        (r'^delete/(?P<schedule_id>\d+)$', 'delete'),
                        (r'^reckless_discard/$', 'reckless_discard'),
)
