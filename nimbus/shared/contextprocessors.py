#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from os import path

def product(request):
    return {'product': settings.NIMBUS_PRODUCT}

def script_name(request):
    return { 'script_name' : request.META['PATH_INFO']}

def menus_from_apps(request):
    apps = settings.MODULAR_APPS
    menu_list = []
    for app in apps:
        if app.startswith('nimbus.'):
            app_name = app.split('.')[-1]
            menu_list.append("%s_menu.html" % app_name)
    return {'menus_from_apps': menu_list}

def block_ie_browser(request):
    # detects browser
    browser = request.META['HTTP_USER_AGENT']
    if re.search("MSIE", browser):
        messages.warning(request, _(u"Incompatible browser. Nimbus tested only Google Chrome and Mozilla Firefox"))
    return {}
