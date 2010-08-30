#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.restore.views',
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^view/$', 'view'), 
    (r'^get_tree/(?P<root>\w+)$', 'get_tree'),
    (r'^get_procedures/(?P<object_id>\d+)/', 'get_procedures'),
    (r'^get_jobs/(?P<computer_id>\d+)/(?P<procedure_id>\d+)/(?P<data_inicio>.*?)/(?P<data_fim>.*?)', 'get_jobs'),
)
