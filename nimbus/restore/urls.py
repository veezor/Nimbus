#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.restore.views',
    (r'^(?P<object_id>\d+)/view/$', 'view'), 
    (r'^view/$', 'view'),
    (r'^step1/$', 'step1'), 
    (r'^step2/$', 'step2'), 
    (r'^step3/$', 'step3'), 
    (r'^step4/$', 'step4'), 
    (r'^step5/$', 'step5'), 
    (r'^step6/$', 'step6'), 
    (r'^teste/$', 'teste'), 
    (r'^restore_files', 'restore_files'),
    (r'^get_tree/$', 'get_tree'),
    (r'^get_client_tree/$', 'get_client_tree'),
    (r'^get_procedures/(?P<object_id>\d+)/', 'get_procedures'),
    (r'^get_jobs/(?P<procedure_id>\d+)/(?P<data_inicio>.*?)/(?P<data_fim>.*?)/', 'get_jobs'),
    (r'^get_tree_search_file/$', 'get_tree_search_file'),
)
