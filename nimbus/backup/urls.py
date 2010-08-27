#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.backup.views',
    (r'^(?P<object_id>\d+)/add/$', 'backup_form'), 
    (r'^add/$', 'backup_form'), 
    # (r'^list/$', 'list'), 
    # (r'^add/$', 'add'), 
    # (r'^(?P<object_id>\d+)/view/$', 'view'), 
    # (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    # (r'^delete/$', 'delete'), 
)
