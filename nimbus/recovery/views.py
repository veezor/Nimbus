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
        'title': u"Recuperação do sistema",
        'page_name': u'offsite',
        'next': "nimbus.recovery.views.recover_databases"
    }

    return edit_singleton_model( request, "generic.html",
                         "nimbus.recovery.views.recover_databases",
                         formclass = OffsiteRecoveryForm,
                         extra_context = extra_context)


def select_storage(request):
    if request.method == "GET":
        extra_content = {
            'wizard_title': u'Selecione o armazenamento',
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
        return render_to_response(request, "recovery_recover_databases.html",
                                  extra_content)
    else:
        raise Http404()


def recover_databases(request):

    logger = logging.getLogger(__name__)
    extra_content = {
        'wizard_title': u'Recuperação do sistema',
        'title': u"Recuperação do sistema",
    }

    if request.method == "GET":
        if not DownloadRequest.objects.count():
            return redirect( 'nimbus.recovery.views.recover_volumes' )

        localsource = request.GET.get("localsource", "offsite")
        device = request.GET.get("device", None)
        extra_content.update({ "localsource" : localsource, "device" : device})
        return render_to_response(request, "recovery_recover_databases.html",
                                  extra_content)

    elif request.method == "POST":
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

            #manager = offsite.LocalManager(storage.mountpoint)

        else:
            manager = offsite.RemoteManager()
            device = None
            localsource = "offsite"


        manager = offsite.RecoveryManager(manager)
        try:
            manager.download_databases()
        except (IOError, pycurl.error), error:
            logger.error('download databases')
            extra_content.update({ "error": error })
            return render_to_response(request,
                    'recovery_instancenameerror.html', extra_content)

        with bacula.BaculaLock() as lock:
            logger.info('Starting database recovery')
            manager.recovery_databases()
            manager.generate_conf_files()
            logger.info('Stoping database recovery')

        extra_content.update({"device" : device, "localsource"  : localsource})

        return render_to_response(request, 'recovery_database_ok.html',  extra_content)

    else:
        raise Http404()


def recover_volumes_worker(manager):
    with bacula.BaculaLock() as lock:
        manager = offsite.RecoveryManager(manager)
        manager.download_volumes()
        manager.finish()


def recover_volumes(request):
    extra_content = {
        'wizard_title': u'Selecione o volume',
        'title': u"Recuperação do sistema",
    }

    if request.method == "GET":
        return render_to_response(request, "recovery_recover_volumes.html", extra_content)
    elif request.method == "POST":
        localsource = request.POST.get("localsource", "offsite")

        if localsource != "offsite":
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            manager = offsite.LocalManager(storage.mountpoint)

        else:
            manager = offsite.RemoteManager()


        systemprocesses.min_priority_job("Recovery nimbus volumes",
                                         recover_volumes_worker, manager)

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
    elif request.method == "POST":
        wizard = Wizard.get_instance()
        wizard.finish()
        return redirect( "nimbus.base.views.home" )
