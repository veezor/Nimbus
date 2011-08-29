#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('nimbus.base.views',
    (r'^$', 'home' ),
    (r'^home/$', 'home' ),
    (r'^ie_error/$', 'ie_error' ),
    (r'^notifications/$', 'notifications' ),
    (r'^ack_notification/$', 'ack_notification' ),
)

