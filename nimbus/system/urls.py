#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.system.views',
    (r'^network_tool/(?P<type>\w+)/$', 'network_tool'), 
    (r'^create_or_view_network_tool/$', 'create_or_view_network_tool'), 
)
