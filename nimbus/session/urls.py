#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import *
from nimbus.session.forms import AuthForm as Form
# from django.contrib.auth.forms import AuthenticationForm

urlpatterns = patterns('django.contrib.auth.views',
    (r'^login/$', 'login', {"template_name" : "login.html", "authentication_form": Form} ),
    (r'^logout/$', 'logout', {"template_name" : "logout.html"} ),
)
