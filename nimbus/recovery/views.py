# -*- coding: utf-8 -*-

import simplejson
import pycurl

import os
import logging

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import redirect
from django.conf import settings

from nimbus.offsite.models import DownloadRequest
from nimbus.shared.views import render_to_response, edit_singleton_model
from nimbus.libs import offsite, systemprocesses, bacula
from nimbus.offsite.models import DownloadRequest
from nimbus.libs.devicemanager import (StorageDeviceManager,
                                       MountError, UmountError)
from nimbus.offsite.forms import OffsiteRecoveryForm
from nimbus.offsite.models import Offsite
from nimbus.wizard.models import Wizard



#def start(request):
#    extra_content = {
#        'title': u"Recuperação do sistema"
#    }
#    return render_to_response(request, "recovery_start.html", extra_content)


def select_source(request):
    extra_content = {
        'wizard_title': u'Selecionar origem',
        'title': u"Recuperação do sistema"
    }

    if request.method == "GET":
        return render_to_response(request, "recovery_select_source.html",
                                  extra_content)
    elif request.method == "POST":
        source = request.POST['source']
        if source == "offsite":
            extra_context = {
                'wizard_title': u'Configuração do Offsite',
                'page_name': u'offsite'
            }
            return redirect( 'nimbus.recovery.views.offsite_recovery' )
        else:
            return redirect( 'nimbus.recovery.views.select_storage' )
    else:
        raise Http404()


def offsite_recovery(request):
    extra_context = {
        'wizard_title': u'Configurar Offsite',
        'title': u'Recuperação do sistema',
        'page_name': u'offsite',
        'next': 'nimbus.recovery.views.recover_databases'
    }

    if request.method == "GET":
        offsite = Offsite.get_instance()
        offsite.active = True
        offsite.save()

    return edit_singleton_model( request, "generic.html",
                         "nimbus.recovery.views.recover_databases",
                         formclass = OffsiteRecoveryForm,
                         extra_context = extra_context)


def select_storage(request):
    if request.method == "GET":
        extra_content = {
            'wizard_title': u'Selecione o armazenamento',
            'title': u"Recuperação do sistema",
            'devices' : offsite.list_disk_labels()
        }
        return render_to_response(request, "recovery_select_storage.html",
                                  extra_content)
    else:
        raise Http404()

def check_database_recover(request):
    count = DownloadRequest.objects.count()
    has_finished = systemprocesses.has_pending_jobs()
    return HttpResponse(simplejson.dumps({"count": count,
                                          "has_finished" : has_finished}))
def recover_databases_worker(manager):
    logger = logging.getLogger(__name__)
    logger.info("iniciando download da base de dados")
    manager.download_databases()
    logger.info("download da base de dados efetuado com sucesso")
    logger.info("iniciando recuperacao da base de dados")
    manager.recovery_databases()
    logger.info("recuperacao da base de dados efetuado com sucesso")
    logger.info("iniciando geracao de arquivos de configuracao")
    manager.generate_conf_files()
    logger.info("geracao dos arquivos de configuracao realizada com sucesso")

def recover_databases(request):
    logger = logging.getLogger(__name__)
    extra_content = {
        'wizard_title': u'Recuperação do sistema',
        'title': u"Recuperação do sistema",
    }

    if request.method == "GET":
        localsource = request.POST.get("localsource", "offsite")

        if localsource != "offsite":
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

            manager = offsite.LocalManager(storage.mountpoint, "/bacula")

        else:
            manager = offsite.RemoteManager()
            device = None
            localsource = "offsite"


        manager = offsite.RecoveryManager(manager)
        logger.info("adicionando trabalho")
        systemprocesses.min_priority_job("Recovery nimbus database",
                                         recover_databases_worker, manager)
        logger.info("trabalho adicionado com sucesso")
        extra_content.update({"device" : device, "localsource"  : localsource})

        return render_to_response(request, "recovery_recover_databases.html", extra_content)

    else:
        raise Http404()


def recover_volumes_worker(manager):
    logger = logging.getLogger(__name__)
    manager = offsite.RecoveryManager(manager)
    logger.info("iniciando download dos volumes")
    manager.download_volumes()
    logger.info("download dos volumes efetuado com sucesso")
    manager.finish()

def check_volume_recover(request):
    count = DownloadRequest.objects.count()
    has_finished = systemprocesses.has_pending_jobs()
    return HttpResponse(simplejson.dumps({"count": count,
                                          "has_finished" : has_finished}))

def recover_volumes(request):
    extra_content = {
        'wizard_title': u'Recuperando arquivos',
        'title': u"Recuperação do sistema",
    }

    if request.method == "GET":
        return render_to_response(request, "recovery_recover_volumes.html", extra_content)
    elif request.method == "POST":
        localsource = request.POST.get("localsource", "offsite")

        if localsource != "offsite":
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            manager = offsite.LocalManager(storage.mountpoint, "/bacula")
        else:
            manager =  offsite.RemoteManager()

        systemprocesses.min_priority_job("Recovery nimbus volumes",
                                         recover_volumes_worker, manager)

        extra_content.update({ "object_list" : DownloadRequest.objects.all()})
        return render_to_response(request, "recovery_recover_volumes.html", extra_content)
    else:
        raise Http404()


def finish(request):
    extra_content = {
        'title': u"Recuperação do sistema",
    }
    if request.method == "GET":
        return render_to_response(request, "recovery_finish.html", extra_content)
    elif request.method == "POST":
        wizard = Wizard.get_instance()
        wizard.finish()
        return redirect( "nimbus.base.views.home" )
