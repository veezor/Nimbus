#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.computers.views',
    (r'^add/$', 'add'), 
    (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    (r'^delete/$', 'delete'), 
    (r'^list/$', 'list'), 
)
