# -*- coding: utf-8 -*-

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages

from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form
from nimbus.libs import offsite
from nimbus.libs.devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)



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



# SECURITY COPY

def security_copy(request):
    title = u"Cópia de segurança"
    return render_to_response(request, "system_security_copy.html", locals())

def select_storage(request):
    # devices = offsite.list_disk_labels()
    devices = ['sda', 'sdb', 'sdc']
    title = u'Cópia de segurança'
    return render_to_response(request, "system_select_storage.html", locals())


def copy_files(request):
    error = None
    device = request.POST.get("device")

    # TODO: Retirar estas duas linhas abaixo.
    messages.success(request, u"O processo foi iniciado com sucesso.")
    return redirect('nimbus.offsite.views.list_uploadrequest')
    
    if not device:
        raise Http404()

    try:
        manager = StorageDeviceManager(device)
        manager.mount()
    except MountError, e:
        error = e

    sizes = [ getsize( dev) for dev in offsite.get_all_bacula_volumes() ]
    required_size = sum( sizes )


    if required_size <  manager.available_size:
        thread = Thread(target=worker_thread, args=(manager,))
        thread.start()
        return redirect('nimbus.offsite.views.list_uploadrequest')
    else:
        required_size = utils.bytes_to_mb(required_size)
        available_size = utils.bytes_to_mb(manager.available_size)
        manager.umount()
        error = u"Espaço necessário é de %.3fMB, somente %.3fMB disponível em %s" %\
                (required_size, available_size, device)

    if error:
        return render_to_response(request, "bkp/offsite/mounterror.html",
                {"error" : error } )
