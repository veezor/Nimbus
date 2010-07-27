#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.timezone.views',
    (r'^config/$', 'timezone_conf'), 
    (r'^ajax_area_request/$', 'area_request'), 
)
