#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.filesets.views',
                       (r'^(?P<fileset_id>\d+)/edit/(?P<computer_id>\d+)$', 'edit'),
                       (r'^add/(?P<computer_id>\d+)$', 'add'),
                       (r'^add/$', 'add'),
                       (r'^get_tree/$', 'get_tree'),
                      )
