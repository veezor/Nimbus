#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.storages.views',
    (r'^$', 'list' ),
    (r'^list/$', 'list' ),
    (r'^add/$', 'add' ),
    (r'^new/$', 'new' ),
    (r'^csv_data/$', 'csv_data' ),
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    (r'^(?P<object_id>\d+)/activate/$', 'activate'), 
    (r'^(?P<object_id>\d+)/deactivate/$', 'deactivate'), 
    
    (r'^(?P<object_id>\d+)/view_computer/$', 'view_computer'), 
)

