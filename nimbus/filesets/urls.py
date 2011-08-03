#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.filesets.views',
                       (r'^(?P<fileset_id>\d+)/edit/(?P<computer_id>\d+)$', 'edit'),
                       (r'^do_add/$', 'do_add'),
                       (r'^(?P<fileset_id>\d+)/do_edit/$', 'do_edit'),
                       (r'^add/(?P<computer_id>\d+)$', 'add'),
                       (r'^add/$', 'add'),
                       (r'^get_tree/$', 'get_tree'),
                       (r'^delete/(?P<fileset_id>\d+)$', 'delete'),
                       (r'^do_delete/(?P<fileset_id>\d+)$', 'do_delete'),
                       (r'^reckless_discard/$', 'reckless_discard'),
                      )
