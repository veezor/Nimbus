#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.backup.views',
    (r'^add/(?P<object_id>\d+)$', 'render'),
    (r'^add/$', 'render'),
    (r'^profiles/add$', 'profile_new'),
    (r'^schedules/add$', 'schedule_new'),
    (r'^filesets/add/(?P<object_id>\d+)$', 'fileset_new'),
    (r'^get_tree/$', 'get_tree'),
    # (r'^list/$', 'list'), 
    # (r'^add/$', 'add'), 
    # (r'^(?P<object_id>\d+)/view/$', 'view'), 
    # (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    # (r'^delete/$', 'delete'), 
)
