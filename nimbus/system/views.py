# -*- coding: utf-8 -*-



import simplejson
from os.path import getsize

from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.core import validators

from devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)

from nimbus.shared.views import render_to_response
from nimbus.shared import utils, middlewares
from nimbus.libs import offsite, systemprocesses, bacula
import networkutils 
import systeminfo


@login_required
def network_tool(request, type="ping"):
    if type == "ping":
        title = u"Teste de ping"
    elif type == "traceroute":
        title = u"Teste de traceroute"
    elif type == "nslookup":
        title = u"Teste de ns lookup"
    
    extra_content = {'title': title, 'type': type}
    
    return render_to_response(request, "system_network_tool.html", extra_content)


@login_required
def create_or_view_network_tool(request):


    if request.method  == "POST":
    
        rtype = request.POST['type']
        ip = request.POST['ip']
        is_url = False

        try:
            try:
                validators.validate_ipv4_address(ip) # ip format x.x.x.x
            except ValidationError, error: # url format www.xxx.xxx
                value = ip
                if not '://' in value:
                    value = 'https://%s' % value
                urlvalidator = validators.URLValidator()
                urlvalidator(value)
                is_url  = True

            if rtype == "ping":
                rcode, output = networkutils.ping(ip)
            elif rtype == "traceroute":
                rcode, output = networkutils.traceroute(ip)
            elif rtype == "nslookup":
                try:
                    if is_url:
                        output = networkutils.resolve_name(ip)
                    else:
                        output = networkutils.resolve_addr(ip)
                except (networkutils.HostAddrNotFound,
                         networkutils.HostNameNotFound), error:
                    output = "Não encontrado"

        except ValidationError, error:
            output = "\n".join(error.messages)
        

        response = simplejson.dumps({'msg': output})
        return HttpResponse(response, mimetype="text/plain")


