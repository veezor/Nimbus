#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.system.views',
    (r'^network_tool/(?P<type>\w+)/$', 'network_tool'), 
    (r'^create_or_view_network_tool/$', 'create_or_view_network_tool'), 
    (r'^stat/$', 'stat'), 
    
    (r'^security_copy/$', 'security_copy'), 
    (r'^select_storage/$', 'select_storage'), 
    (r'^copy_files/$', 'copy_files'), 
)
