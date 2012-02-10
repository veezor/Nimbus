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
    (r'^self_auth', 'self_auth'), # WORKAROUND enquanto a central não informa o host do servidor de storage
    (r'^list_procedures', 'list_procedures'),
    (r'^list_offsite/$', 'list_offsite'),
    (r'^upload_queue/$', 'upload_queue'),
    (r'^upload_queue_data/$', 'upload_queue_data'),
)


