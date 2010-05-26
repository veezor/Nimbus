#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os.path import join, getsize
from threading import Thread

from django.http import Http404

from devicemanager import StorageDeviceManager, MountError

from backup_corporativo.bkp.views import allow_get, allow_post, render
from backup_corporativo.bkp import models, offsite, utils





@allow_get
def select_storage(request):
    return render(request, "bkp/offsite/select_storage.html",
                    {"devices" : offsite.list_disk_labels() })





def worker_thread(storage_manager):
    manager = offsite.LocalManager(origin=None,
                                  destination=storage_manager.mountpoint)
    manager.upload_all_volumes()
    storage_manager.umount()


@allow_post
def copy_files_to_storage(request):

    error = None
    device = request.POST.get("device")


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
        return utils.redirect('list_uploadrequest')
    else:
        required_size = utils.bytes_to_mb(required_size)
        available_size = utils.bytes_to_mb(manager.available_size)
        manager.umount()
        error = u"Espaço necessário é de %.3fMB, somente %.3fMB disponível em %s" %\
                (required_size, available_size, device)

    if error:
        return render(request, "bkp/offsite/mounterror.html",
                {"error" : error } )




@allow_get
def list_downloadrequest(request):
    return render(request, "bkp/offsite/list_downloadrequest.html", 
                  {"object_list": models.DownloadRequest.objects.all()})

@allow_get
def list_uploadrequest(request):
    return render(request, "bkp/offsite/list_uploadrequest.html", 
                  {"object_list": models.UploadRequest.objects.all()})




