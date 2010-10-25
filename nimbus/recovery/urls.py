#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.recovery.views',
    (r'^start/$', 'start'), 
    (r'^select_source/$', 'select_source'), 
    (r'^select_storage/$', 'select_storage'), 
    (r'^select_instance_name/$', 'select_instance_name'), 
    (r'^recover_databases/$', 'recover_databases'), 
    (r'^recover_volumes/$', 'recover_volumes'), 
    (r'^finish/$', 'finish'), 
)
