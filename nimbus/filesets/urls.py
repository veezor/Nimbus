#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.filesets.views',
                       (r'^(?P<object_id>\d+)/edit/$', 'edit'),
                       (r'^add/(?P<object_id>\d+)$', 'add'),
                       (r'^add/$', 'add'),
                       (r'^get_tree/$', 'get_tree'),
                      )
