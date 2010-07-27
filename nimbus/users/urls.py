#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf.urls.defaults import *

urlpatterns = patterns('django.contrib.auth.views',
    (r'^password_change/$', 'password_change', 
        {"template_name" : "password_change.html"}),
    (r'^password_change_done/$', 'password_change_done', 
        {"template_name" : "password_change_done.html"}),
)
