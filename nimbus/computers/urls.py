#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.computers.views',
    (r'^$', 'list'), 
    (r'^list/$', 'list'), 
    (r'^add/$', 'add'), 
    (r'^new/$', 'new'), 
    (r'^check_my_status/$', 'check_my_status'), 
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^(?P<object_id>\d+)/edit/$', 'edit'), 
    (r'^(?P<object_id>\d+)/edit_no_active/$', 'edit_no_active'),
    (r'^(?P<object_id>\d+)/delete/$', 'delete'),
    (r'^(?P<object_id>\d+)/do_delete/$', 'do_delete'),
    
    (r'^delete/$', 'delete'), 
    (r'^group/add/$', 'group_add'), 
    (r'^group/list/$', 'group_list'), 
    
    (r'^(?P<object_id>\d+)/activate/$', 'activate'), 
    (r'^(?P<object_id>\d+)/deactivate/$', 'deactivate'),
    (r'^(?P<object_id>\d+)/configure/$', 'configure')
)
