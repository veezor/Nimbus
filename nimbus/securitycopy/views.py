#!/usr/bin/env python
# -*- coding: UTF-8 -*-



from os.path import getsize
import simplejson


from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from nimbus.shared import utils, middlewares
from nimbus.shared.views import render_to_response
from nimbus.libs import systemprocesses, bacula
from nimbus.offsite import managers as offsite
from devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)
import systeminfo



def upload_volumes_worker(storage_manager):
    with bacula.BaculaLock() as lock:
        manager = offsite.LocalManager(origin=None,
                                      destination=storage_manager.mountpoint)
        manager.upload_all_volumes()
        storage_manager.umount()


@login_required
def stat(request):
    memory = systeminfo.get_memory_usage()
    memory_free = 100 - memory
    extra_content = {
        'title': u"Estatística do sistema",
        'cpu' : systeminfo.get_cpu_usage(),
        'memory' : memory,
        'memory_free' : memory_free
    }

    return render_to_response(request, "stat.html", extra_content)



@login_required
def umount(request):
    if request.method == "GET":
        devices = offsite.list_disk_labels()
        title = u'Remover dispositivo externo com segurança'
        return render_to_response(request, "umount_storage.html", locals())

    if request.method == "POST":
        device = request.POST.get("device")

        try:
            manager = StorageDeviceManager(device)
            manager.umount()
        except UmountError, e:
            error = e
            messages.error(request, u"Erro ao remover unidade")

        messages.success(request, u"Unidade removida corretamente.")
        return redirect('nimbus.base.views.home')


# SECURITY COPY


@login_required
def security_copy(request):
    title = u"Cópia de segurança"
    return render_to_response(request, "system_security_copy.html", locals())


@login_required
def select_storage(request):
    devices = offsite.list_disk_labels()
    title = u'Cópia de segurança'
    return render_to_response(request, "system_select_storage.html", locals())


@login_required
def copy_files(request):

    if request.method == "POST":
        error = None
        device = request.POST.get("device")

        if not device:
            raise Http404()

        try:
            manager = StorageDeviceManager(device)
            manager.mount()
        except (MountError, OSError), e:
            error = e
            messages.error(request, "Impossível montar dispositivo. Sistema de arquivo inadequado")
            return redirect('nimbus.system.views.select_storage')


        sizes = [ getsize( dev) for dev in offsite.get_all_bacula_volumes() ]
        required_size = sum( sizes )


        if required_size <  manager.available_size:
            systemprocesses.min_priority_job("Nimbus upload volumes",
                                             upload_volumes_worker, manager)
            messages.success(request, u"O processo foi iniciado com sucesso.")
            return redirect('nimbus.offsite.views.list_uploadrequest')
        else:
            required_size = utils.bytes_to_mb(required_size)
            available_size = utils.bytes_to_mb(manager.available_size)
            manager.umount()
            error_msg = u"Espaço necessário é de %.3fMB, somente %.3fMB disponível em %s" %\
                    (required_size, available_size, device)
            messages.error(request, error_msg)
            return redirect('nimbus.system.views.select_storage')



@login_required
def pid_history(request):

    threadpool = middlewares.ThreadPool.get_instance()
    jobs = threadpool.list_jobs_pending()

    if 'ajax' in request.POST:
        l = []
        for job in jobs:
            d = {}
            d['pk'] = job.id
            d['fields'] = {}
            d['fields']['pid'] = job.id
            d['fields']['created_at'] = job.created_at.strftime("%d/%m/%Y %H:%M")
            d['fields']['name'] = job.description
            d['fields']['status'] = job.status
            l.append(d)
        response = simplejson.dumps(l)
        return HttpResponse(response, mimetype="text/plain")

    return render_to_response( request,
                               "pid_history.html",
                               {"object_list": jobs,
                                "list_type": "Downloads",
                                "title": u"Processos"})
