#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.offsite.views',
    (r'^detail', 'detail'),
    (r'^edit', 'edit'),
    (r'^list_uploadrequest', 'list_uploadrequest'),
    (r'^self_auth', 'self_auth'), # WORKAROUND enquanto a central não informa o host do servidor de storage
    (r'^list_procedures', 'list_procedures')
)


