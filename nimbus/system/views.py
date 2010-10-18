# -*- coding: utf-8 -*-

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from django.core import validators

from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form
from nimbus.libs import offsite
from nimbus.libs.devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)
import networkutils 




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


    if request.method  == "POST":
    
        type = request.POST['type']
        ip = request.POST['ip']
        is_url = False

        try:
            validators.validate_ipv4_address(ip) # ip format x.x.x.x
        except ValidationError, error: # url format www.xxx.xxx
            value = ip
            if not '://' in value:
                value = 'https://%s' % value
            urlvalidator = validators.URLValidator()
            urlvalidator(value)
            is_url  = True
        
        if type == "ping":
            rcode, output = networkutils.ping(ip)
        elif type == "traceroute":
            rcode, output = networkutils.traceroute(ip)
        elif type == "nslookup":
            if is_url:
                output = networkutils.resolve_name(ip)
            else:
                output = networkutils.resolve_addr(ip)

        response = simplejson.dumps({'msg': output})
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
