#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('nimbus.network.views',
    (r'^config/$', 'network_conf'), 
    (r'^redirect_after_update/$', 'redirect_after_update'),
)


