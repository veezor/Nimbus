#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.remotestorages.views',
    (r'^(?P<object_id>\d+)/view/$', 'render'),
    (r'^(?P<object_id>\d+)/warnning_alert/$', 'warnning_alert'),
    (r'^(?P<object_id>\d+)/critical_alert/$', 'critical_alert'),
    (r'^$', 'render')
)
