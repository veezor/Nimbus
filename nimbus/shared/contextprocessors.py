#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from django.contrib import messages


def script_name(request):
    return { 'script_name' : request.META['PATH_INFO']}



def block_ie_browser(request):
    # detects browser
    browser = request.META['HTTP_USER_AGENT']
    if re.search("MSIE", browser):
        messages.warning(request, "Navegador incompativel com o Nimbus. Sistema testado apenas para Google Chrome e Mozilla Firefox.")
    return {}
