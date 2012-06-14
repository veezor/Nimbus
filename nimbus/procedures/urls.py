#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.procedures.views',
                        (r'^add/$', 'add'),
                        (r'^add/', 'add'),
                        (r'^list/$', 'list_all'),
                        (r'^history/$', 'history'),
                        (r'^(?P<object_id>\d+)/history/$', 'history'),
                        # # (r'^(?P<object_id>\d+)/view/$', 'view'),
                        (r'^(?P<procedure_id>\d+)/edit/$', 'edit'),
                        (r'^(?P<object_id>\d+)/delete/$', 'delete'),
                        (r'^(?P<object_id>\d+)/do_delete/$', 'do_delete'),
                        (r'^(?P<object_id>\d+)/activate/$', 'activate'),
                        (r'^(?P<object_id>\d+)/deactivate/$', 'deactivate'),
                        (r'^(?P<object_id>\d+)/execute/$', 'execute'),
                        (r'^(?P<job_id>\d+)/cancel_job/$', 'cancel_job'),
                        # (r'^profile/$', 'profile_list'),
                        (r'^profile/list/$', 'profile_list'),
                        # (r'^profile/add/$', 'profile_add'),
                        # (r'^profile/(?P<object_id>\d+)/edit/$', 'profile_edit'),
                        # (r'^profile/(?P<object_id>\d+)/delete/$', 'profile_delete'),
                                           

)


