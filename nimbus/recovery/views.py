# -*- coding: utf-8 -*-

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.offsite.models import DownloadRequest
from nimbus.shared.views import render_to_response
from nimbus.libs import offsite
from nimbus.libs.devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)


from django.http import HttpResponse, HttpResponseRedirect, Http404


def start(request):
    extra_content = {
        'title': u"Recuperação do sistema"
    }
    return render_to_response(request, "recovery_start.html", extra_content)


def select_source(request):
    extra_content = {
        'title': u"Recuperação do sistema"
    }
    
    if request.method == "GET":
        return render_to_response(request, "recovery_select_source.html",
                                  extra_content)
    elif request.method == "POST":
        source = request.POST['source']
        if source == "offsite":
            return redirect( 'nimbus.recovery.views.select_instance_name' )
        else:
            return redirect( 'nimbus.recovery.views.select_storage' )
    else:
        raise Http404()


def select_storage(request):
    if request.method == "GET":
        extra_content = {
            'title': u"Recuperação do sistema",
             "devices" : offsite.list_disk_labels()
        }
        return render_to_response(request, "recovery_select_storage.html",
                                  extra_content)
    elif request.method == "POST":
        localsource = request.POST.get("localsource", True)
        device = request.POST.get("device", None)
        extra_content = {
            'title': u"Recuperação do sistema",
            "localsource" : localsource,
            "device" : device
        }
        return render_to_response(request, "recovery_confirm_storage.html",
                                  extra_content)
    else:
        raise Http404()



def select_instance_name(request):
    if request.method == "GET":

        localsource = request.GET.get("localsource", None)
        device = request.GET.get("device", None)

        if localsource:
            storage = StorageDeviceManager(device)
            manager = offsite.LocalManager(storage.mountpoint)
            storage.mount()
        else:
            manager = offsite.RemoteManager()

        manager = offsite.RecoveryManager()

        instance_names = manager.get_instance_names()
        manager.finish()


        return render_to_response(request, "recovery_select_instance_name.html",
                     { "localsource" : localsource, "device" : device, 
                       "instance_names" : instance_names })

    elif request.method == "POST":
        localsource = request.POST.get("localsource", None)
        device = request.POST.get("device", None)
        return render_to_response(request, "recovery_change_instance_name.html",
                     { "localsource" : localsource, "device" : device})
    else:
        raise Http404()



def recover_databases(request):
    extra_content = {
        'title': u"Recuperação do sistema",
    }
    
    if request.method == "GET":

        localsource = request.GET.get("localsource", None)
        device = request.GET.get("device", None)
        extra_content.update({ "localsource" : localsource, "device" : device})
        return render_to_response(request, "recovery_recover_databases.html",
                                  extra_content)

    elif request.method == "POST":
        localsource = request.POST.get("localsource", None)
        
        if localsource:
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            try:
                storage.mount()
            except MountError, error:
                extra_content.update({ "error": error, 
                   "device" : device, 
                   "localsource"  : True})
                return render_to_response(request, 'recovery_mounterror.html', 
                                          extra_content)
        
            manager = offsite.LocalManager(storage.mountpoint)
        
        else:
            manager = offsite.RemoteManager()
        
        
        
        manager = offsite.RecoveryManager(manager)
        try:
            manager.download_databases()
        except (IOError, pycurl.error), error:
            extra_content.update({ "error": error, 
               "device" : device, 
               "localsource"  : True})
            return render_to_response(request,
                    'recovery_instancenameerror.html', extra_content)
        
        manager.recovery_databases()
        manager.generate_conf_files()
        
        extra_content.update({"device" : device, "localsource"  : True})
        return render_to_response(request, 'recovery_database_ok.html',  extra_content)

    else:
        raise Http404()



def worker_thread(manager):
    manager = offsite.RecoveryManager(manager)
    manager.download_volumes()
    manager.finish()


def recover_volumes(request):
    extra_content = {
        'title': u"Recuperação do sistema",
    }
    
    if request.method == "GET":
        return render_to_response(request, "recovery_recover_volumes.html", extra_content)
    elif request.method == "POST":
        localsource = request.POST.get("localsource", None)
        
        if localsource:
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            manager = offsite.LocalManager(storage.mountpoint)
        
        else:
            manager = offsite.RemoteManager()
        
        
        worker = Thread(target=worker_thread, args=(manager,))
        worker.start()
        
        extra_content.update({ "object_list" : DownloadRequest.objects.all()})
        return render_to_response(request,
                "recovery_list_downloads.html",
                extra_content)
    else:
        raise Http404()


def finish(request):
    extra_content = {
        'title': u"Recuperação do sistema",
    }
    if request.method == "GET":
        return render_to_response(request, "recovery_finish.html", extra_content)
