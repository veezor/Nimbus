#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.securitycopy.views',
    (r'^stat/$', 'stat'),
    (r'^umount/$', 'umount'),
    (r'^security_copy/$', 'security_copy'),
    (r'^select_storage/$', 'select_storage'),
    (r'^copy_files/$', 'copy_files'),
    (r'^pid_history/$', 'pid_history'),
)
