#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.storages.views',
    (r'^$', 'list' ),
    (r'^list/$', 'list' ),
    (r'^add/$', 'add' ),
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
)

