
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from environment import ENV
import keymanager

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.views import global_vars, authentication_required

@authentication_required
def view_tools(request):
    E = ENV(request)

    if request.method == 'GET':
        E.template = 'bkp/tools/index_tools.html'
        return E.render()

@authentication_required
def tools_ssl(request):
    E = ENV(request)

    if request.method == 'GET':
        E.rsa, E.cert, E.pem = keymanager.generate_keys_as_text()
        E.template = 'bkp/tools/tools_ssl.html'
        return E.render()