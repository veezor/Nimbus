#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.recovery.views',
    (r'^select_source/$', 'select_source'),
    (r'^select_storage/$', 'select_storage'),
    (r'^recover_databases/$', 'recover_databases'),
    (r'^check_database_recover/$', 'check_database_recover'),
    (r'^recover_volumes/$', 'recover_volumes'),
    (r'^check_volume_recover/$', 'check_volume_recover'),
    (r'^offsite_recovery/$', 'offsite_recovery'),
    (r'^finish/$', 'finish'),
)
