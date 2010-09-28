# -*- coding: utf-8 -*-

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form

from django.http import HttpResponse, HttpResponseRedirect



def network_tool(request, type="ping"):
    if type == "ping":
        title = u"Teste de ping"
    elif type == "traceroute":
        title = u"Teste de traceroute"
    elif type == "nslookup":
        title = u"Teste de ns lookup"
    
    extra_content = {'title': title, 'type': type}
    
    return render_to_response(request, "system_network_tool.html", extra_content)


def create_or_view_network_tool(request):
    import time
    time.sleep(1)
    
    type = request.POST['type']
    ip = request.POST['ip']
    
    if type == "ping":
        output = """PING [ip] ([ip]): 56 data bytes
        64 bytes from [ip]: icmp_seq=0 ttl=64 time=3.063 ms
        64 bytes from [ip]: icmp_seq=1 ttl=64 time=1.295 ms
        64 bytes from [ip]: icmp_seq=2 ttl=64 time=3.027 ms
        64 bytes from [ip]: icmp_seq=3 ttl=64 time=3.252 ms
        64 bytes from [ip]: icmp_seq=4 ttl=64 time=3.150 ms

        --- [ip] ping statistics ---
        5 packets transmitted, 5 packets received, 0.0% packet loss
        round-trip min/avg/max/stddev = 1.295/2.757/3.252/0.735 ms
        """
    elif type == "traceroute":
        output = """traceroute to [ip] ([ip]), 64 hops max, 52 byte packets
         1  [ip]  2.984 ms  1.952 ms  0.970 ms
        """
    elif type == "nslookup":
        output = """Server:		192.168.10.2
        Address:	192.168.10.2#53

        Non-authoritative answer:
        Name:	[ip]
        Address: 89.18.179.41
        """
    
    response = simplejson.dumps({'msg': output.replace('[ip]', ip)})
    return HttpResponse(response, mimetype="text/plain")

def stat(request):
    extra_content = {'title': u"Estatística do sistema"}

    return render_to_response(request, "stat.html", extra_content)