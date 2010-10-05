#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.recovery.views',
    (r'^start/$', 'recovery_start'), 
    (r'^select_source/$', 'recovery_select_source'), 
    (r'^select_storage/$', 'recovery_select_storage'), 
    (r'^select_instance_name/$', 'recovery_select_instance_name'), 
    (r'^recover_databases/$', 'recover_databases'), 
    (r'^recover_volumes/$', 'recover_volumes'), 
    (r'^volumes/$', 'recover_volumes'), 
    (r'^finish/$', 'recovery_finish'), 
)
