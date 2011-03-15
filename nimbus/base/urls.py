#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.base.views',
    (r'^$', 'home' ),
    (r'^home/$', 'home' ),
)

