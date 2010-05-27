#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Thread

import pycurl

from django.http import Http404

from backup_corporativo.bkp import utils, models, offsite
from backup_corporativo.bkp.views import render


from devicemanager import StorageDeviceManager, MountError


def recovery_start(request):
    return render(request, "bkp/recovery/start.html", {})


def recovery_select_source(request):
    if request.method == "GET":
        return render(request, "bkp/recovery/select_source.html", {})
    elif request.method == "POST":
        source = request.POST['source']
        if source == "offsite":
            return utils.redirect( 'recover_databases' )
        else:
            return utils.redirect( 'recovery_select_storage' )
    else:
        raise Http404()



def recovery_select_storage(request):
    if request.method == "GET":
        return render(request, "bkp/recovery/select_storage.html",
                        {"devices" : offsite.list_disk_labels() })
    elif request.method == "POST":
        localsource = request.POST.get("localsource", True)
        device = request.POST.get("device", None)
        return render(request, "bkp/recovery/confirm_storage.html",
                     { "localsource" : localsource, "device" : device})
    else:
        raise Http404()
    


def recovery_select_instance_name(request):
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

            
        return render(request, "bkp/recovery/select_instance_name.html",
                     { "localsource" : localsource, "device" : device, 
                       "instance_names" : instance_names })

    elif request.method == "POST":
        localsource = request.POST.get("localsource", None)
        device = request.POST.get("device", None)
        return render(request, "bkp/recovery/change_instance_name.html",
                     { "localsource" : localsource, "device" : device})
    else:
        raise Http404()



def recover_databases(request):
    if request.method == "GET":

        localsource = request.GET.get("localsource", None)
        device = request.GET.get("device", None)
            
        return render(request, "bkp/recovery/recover_databases.html",
                     { "localsource" : localsource, "device" : device})

    elif request.method == "POST":
        localsource = request.POST.get("localsource", None)

        if localsource:
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            try:
                storage.mount()
            except MountError, error:
                return render(request, 'bkp/recovery/mounterror.html', 
                             { "error": error, 
                               "device" : device, 
                               "localsource"  : True})

            manager = offsite.LocalManager(storage.mountpoint)

        else:
            manager = offsite.RemoteManager()



        manager = offsite.RecoveryManager(manager)
        try:
            manager.download_databases()
        except (IOError, pycurl.error), error:
            return render(request, 'bkp/recovery/instancenameerror.html', 
                         { "error": error, 
                           "device" : device, 
                           "localsource"  : True})

        manager.recovery_databases()
        manager.generate_conf_files()
        return render(request, 'bkp/recovery/databasesok.html', 
                      {"device" : device, "localsource"  : True})
            
    else:
        raise Http404()



def worker_thread(manager):
    manager = offsite.RecoveryManager(manager)
    manager.download_volumes()
    manager.finish()


def recover_volumes(request):
    if request.method == "GET":
        return render(request, "bkp/recovery/recover_volumes.html",
                      {})
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

        return render(request, "bkp/recovery/recover_list_downloads.html",
                { "object_list" : models.DownloadRequest.objects.all()})
    else:
        raise Http404()


def recovery_finish(request):
    if request.method == "GET":
        return render(request, "bkp/recovery/finish.html",
                      {})
