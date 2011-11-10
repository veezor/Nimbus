# -*- coding: utf-8 -*-

import simplejson
import logging

from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from devicemanager import StorageDeviceManager, MountError

from nimbus.shared.views import render_to_response
from nimbus.libs import systemprocesses
from nimbus.offsite import managers as offsite
from nimbus.offsite.models import DownloadRequest
from nimbus.wizard.models import Wizard
from nimbus.wizard.views import only_wizard

#def start(request):
#    extra_content = {
#        'title': u"Recuperação do sistema"
#    }
#    return render_to_response(request, "recovery_start.html", extra_content)



@only_wizard
def recovery(request):
    extra_context = {
        'wizard_title': u'Recuperação do sistema',
        'page_name': u'recovery',
        'next': reverse('nimbus.wizard.views.timezone')
    }
    if request.method == "GET":
        return render_to_response( request, "recovery.html", extra_context )
    elif request.method == "POST":
        return redirect('nimbus.recovery.views.select_source')
    else:
        raise Http404()




@only_wizard
def select_source(request):
    extra_content = {'wizard_title': u'Selecionar origem',
                     'title': u"Recuperação do sistema"}
    if request.method == "GET":
        return render_to_response(request, "recovery_select_source.html",
                                  extra_content)
    elif request.method == "POST":
        source = request.POST['source']
        if source == "offsite":
            extra_context = {'wizard_title': u'Configuração do Offsite',
                             'page_name': u'offsite'}
            return redirect('nimbus.recovery.views.recover_databases')
        else:
            return redirect('nimbus.recovery.views.select_storage')
    else:
        raise Http404()


@only_wizard
def select_storage(request):
    if request.method == "GET":
        extra_content = {'wizard_title': u'Selecione o armazenamento',
                         'title': u"Recuperação do sistema",
                         'devices' : offsite.list_disk_labels()}
        return render_to_response(request, "recovery_select_storage.html",
                                  extra_content)
    else:
        raise Http404()


@only_wizard
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



@only_wizard
def recover_databases(request):
    logger = logging.getLogger(__name__)
    extra_content = {'wizard_title': u'Recuperação do sistema',
                     'title': u"Recuperação do sistema"}
    if request.method == "GET":
        manager = offsite.RemoteManager()
    elif request.method == "POST":
        localsource = request.POST.get("localsource", "offsite")
        if localsource != "offsite":
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            try:
                storage.mount()
            except MountError, error:
                extra_content.update({"error": error,
                                      "device" : device,
                                      "localsource"  : True})
                return render_to_response(request, 'recovery_mounterror.html',
                                          extra_content)
            manager = offsite.LocalManager(storage, "/bacula")
    manager = offsite.RecoveryManager(manager)
    logger.info("adicionando trabalho")
    systemprocesses.min_priority_job("Recovery nimbus database",
                                     recover_databases_worker, manager)
    logger.info("trabalho adicionado com sucesso")
    extra_content.update({"device" : device, "localsource"  : localsource})
    return render_to_response(request, "recovery_recover_databases.html",
                              extra_content)

def recover_volumes_worker(manager):
    logger = logging.getLogger(__name__)
    manager = offsite.RecoveryManager(manager)
    logger.info("iniciando download dos volumes")
    manager.download_volumes()
    logger.info("download dos volumes efetuado com sucesso")
    manager.finish()



@only_wizard
def check_volume_recover(request):
    count = DownloadRequest.objects.count()
    has_finished = systemprocesses.has_pending_jobs()
    return HttpResponse(simplejson.dumps({"count": count,
                                          "has_finished" : has_finished}))

@only_wizard
def recover_volumes(request):
    extra_content = {'wizard_title': u'Recuperando arquivos',
                     'title': u"Recuperação do sistema"}
    if request.method == "GET":
        return render_to_response(request, "recovery_recover_volumes.html",
                                  extra_content)
    elif request.method == "POST":
        localsource = request.POST.get("localsource", "offsite")
        if localsource != "offsite":
            device = request.POST.get("device")
            storage = StorageDeviceManager(device)
            manager = offsite.LocalManager(storage, "/bacula")
        else:
            manager =  offsite.RemoteManager()
        systemprocesses.min_priority_job("Recovery nimbus volumes",
                                         recover_volumes_worker, manager)
        extra_content.update({ "object_list" : DownloadRequest.objects.all()})
        return render_to_response(request, "recovery_recover_volumes.html", extra_content)
    else:
        raise Http404()



@only_wizard
def finish(request):
    extra_content = {'title': u"Recuperação do sistema"}
    if request.method == "GET":
        return render_to_response(request, "recovery_finish.html", extra_content)
    elif request.method == "POST":
        wizard = Wizard.get_instance()
        wizard.finish()
        return redirect( "nimbus.base.views.home" )
