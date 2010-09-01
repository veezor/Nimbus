#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.procedures.views',
    (r'^$', 'list'), 
    (r'^list/$', 'list'), 
    (r'^list_offsite/$', 'list_offsite'), 
)
