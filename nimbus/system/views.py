# -*- coding: utf-8 -*-

import simplejson

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from nimbus.shared.views import render_to_response
import networkutils


@login_required
def network_tool(request, type="ping"):
    if type == "ping":
        title = _(u"Ping")
    elif type == "traceroute":
        title = _(u"Traceroute")
    elif type == "nslookup":
        title = _(u"NS Lookup")
    
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
                    output = _("Not found")

        except ValidationError, error:
            output = "\n".join(error.messages)
        

        response = simplejson.dumps({'msg': output})
        return HttpResponse(response, mimetype="text/plain")


