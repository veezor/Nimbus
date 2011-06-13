#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.remotestorages.views',
    (r'^(?P<object_id>\d+)/view/$', 'render'),
    (r'^$', 'render')
)
