#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.reports.views',
    (r'^email_conf/$', 'email_conf'),
    (r'^email_test/$', 'email_test'),
)
