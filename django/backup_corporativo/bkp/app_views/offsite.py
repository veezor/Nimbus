#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os.path import join

from django.http import Http404

from backup_corporativo.bkp.views import allow_get, allow_post, render
from backup_corporativo.bkp import models, offsite, utils
from threading import Thread




@allow_get
def select_storage(request):
    return render(request, "bkp/offsite/select_storage.html",
                    {"devices" : offsite.list_disk_labels() })





def worker_thread(storage):
    archive_devices = offsite.find_archive_devices()
    for arc_dev in archive_devices:
        dest = join( "/media" , storage )
        manager = offsite.LocalManager(origin=arc_dev, 
                                       destination=dest)
        manager.upload_all_volumes()


@allow_post
def copy_files_to_storage(request):

    device = request.POST.get("device")

    if not device:
        raise Http404()

    thread = Thread(target=worker_thread, args=(device,))
    thread.start()

    return utils.redirect('list_uploadrequest')


@allow_get
def list_downloadrequest(request):
    return render(request, "bkp/offsite/list_downloadrequest.html", 
                  {"object_list": models.DownloadRequest.objects.all()})

@allow_get
def list_uploadrequest(request):
    return render(request, "bkp/offsite/list_uploadrequest.html", 
                  {"object_list": models.UploadRequest.objects.all()})




