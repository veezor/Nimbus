#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.offsite.views',
    (r'^detail', 'detail'),
    (r'^edit', 'edit'),
    (r'^list_downloadrequest', 'list_downloadrequest'),
    (r'^list_uploadrequest', 'list_uploadrequest'),
    (r'^select_storage', 'select_storage'),
    (r'^copy_files_to_storage', 'copy_files_to_storage'),
    (r'^list_procedures', 'list_procedures')
)


