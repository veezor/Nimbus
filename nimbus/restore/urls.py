#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.restore.views',
    (r'^$', 'list'), 
    # (r'^list/$', 'list'), 
    # (r'^add/$', 'add'), 
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^get_tree/(?P<root>\w+)$', 'get_tree'), 
    # (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    # (r'^delete/$', 'delete'), 
)
