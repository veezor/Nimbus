#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('django.contrib.auth.views',
    (r'^login/$', 'login', {"template_name" : "login.html"} ),
    (r'^logout/$', 'logout', {"template_name" : "logout.html"} ),
)

