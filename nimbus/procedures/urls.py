#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.procedures.views',
                        (r'^add/$', 'add'),
                        (r'^add/', 'add'),
                        (r'^$', 'list_all'), 
                        (r'^list/$', 'list_all'), 
                        # # (r'^(?P<object_id>\d+)/view/$', 'view'), 
                        (r'^(?P<procedure_id>\d+)/edit/$', 'edit'),
                        (r'^(?P<object_id>\d+)/delete/$', 'delete'),
                        (r'^(?P<object_id>\d+)/activate/$', 'activate'),
                        (r'^(?P<object_id>\d+)/deactivate/$', 'deactivate'),
                        #     
                        (r'^list_offsite/$', 'list_offsite'),
                        # (r'^(?P<object_id>\d+)/activate_offsite/$', 'activate_offsite'), 
                        # (r'^(?P<object_id>\d+)/deactivate_offsite/$', 'deactivate_offsite'), 
                        #     
                        (r'^(?P<object_id>\d+)/execute/$', 'execute'),
                        #     
                        # (r'^profile/$', 'profile_list'),
                        (r'^profile/list/$', 'profile_list'),
                        # (r'^profile/add/$', 'profile_add'),
                        # (r'^profile/(?P<object_id>\d+)/edit/$', 'profile_edit'),
                        # (r'^profile/(?P<object_id>\d+)/delete/$', 'profile_delete'),
)
