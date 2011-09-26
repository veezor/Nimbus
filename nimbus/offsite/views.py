# -*- coding: utf-8 -*-

from urllib2 import URLError
from os.path import join
from datetime import datetime
import simplejson

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nimbus.libs import offsite, systemprocesses
from nimbus.offsite.models import (LocalUploadRequest, 
                                   RemoteUploadRequest, 
                                   DownloadRequest)
from nimbus.procedures.models import Procedure
from nimbus.offsite.models import Offsite
from nimbus.shared import utils
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.offsite.forms import OffsiteForm
from nimbus.libs.graphsdata import GraphDataManager


@login_required
def detail(request):
    offsite = Offsite.objects.get(id=1)
    uploads = list(LocalUploadRequest.objects.all()) + list(RemoteUploadRequest.objects.all())
    content = []
    for upload in uploads:
        content.append({'type' : 'ok',
                        'date' : upload.last_attempt or upload.created_at,
                        'label' : upload.volume.filename,
                        'message' : "%.2f MB" % utils.bytes_to_mb(upload.volume.size)
                       })
    transferencias_em_execucao = [{'title': u'Transferências em execução',
                                   'content': content}]
    offsite = Offsite.get_instance()
    if offsite.active:
        try:
            graph_data_manager = GraphDataManager()
            data = graph_data_manager.list_offsite_measures()
            if data:
                usage = graph_data_manager.list_offsite_measures()[-1][-1]
                ocupacao_offsite =  usage / float(offsite.plan_size)
                # [(date, value),...]
            else:
                ocupacao_offsite = 0.0
                messages.warning(request, "Dados não disponíveis. Aguarde sincronização com o offsite")
        except URLError, error:
            messages.error(request, "Erro na conexão com o backup nas nuvens. Verifique conexão.")
            ocupacao_offsite = 0.0
    else:
        ocupacao_offsite = 0.0
        messages.error(request, "Offsite desativado")
    return render_to_response(request, "detail.html", locals())

@login_required
def edit(request):
    title = u'Editar configurações do offsite'
    return edit_singleton_model(request, "offsite_edit.html", 
                                "nimbus.offsite.views.detail",
                                formclass = OffsiteForm,
                                extra_context = locals())

@login_required
def select_storage(request):
    return render_to_response(request, 
                              "select_storage.html",
                              {"devices" : offsite.list_disk_labels()})

def copy_files_worker(storage):
    archive_devices = offsite.find_archive_devices()
    for arc_dev in archive_devices:
        dest = join("/media" , storage)
        manager = offsite.LocalManager(origin=arc_dev, destination=dest)
        manager.upload_all_volumes()

@login_required
def copy_files_to_storage(request):
    if request.method == "POST":
        device = request.POST.get("device")
        if not device:
            raise Http404()
        systemprocesses.min_priority_job("Nimbus volumes copy to disk", 
                                         copy_files_worker, device)
        return redirect('nimbus.offsite.views.list_uploadrequest')
    else:
        return redirect('nimbus.offsite.views.list_uploadrequest')

@login_required
def list_downloadrequest(request):
    downloads_requests = DownloadRequest.objects.all()
    if 'ajax' in request.POST:
        l = []
        for down in downloads_requests:
            d = {}
            d['pk'] = down.id
            # d['model'] = down.model
            d['fields'] = {}
            d['fields']['filename'] = down.volume.filename
            d['fields']['created_at'] = datetime.strftime(down.created_at,
                                                          "%d/%m/%Y %H:%M")
            d['fields']['attempts'] = down.attempts
            if down.last_attempt:
                d['fields']['last_attempt'] = down.last_attempt.strftime("%d/%m/%Y %H:%M")
            else:
                d['fields']['last_attempt'] = None
            d['fields']['friendly_rate'] = down.friendly_rate
            d['fields']['estimated_transfer_time'] = down.estimated_transfer_time
            d['fields']['finished_percent'] = down.finished_percent
            l.append(d)
        # response = serializers.serialize("json", downloads_requests)
        response = simplejson.dumps(l)
        return HttpResponse(response, mimetype="text/plain")
    return render_to_response(request, 
                              "list_downuploadrequest.html", 
                              {"object_list": downloads_requests,
                               "list_type": "Downloads",
                               "title": u"Downloads ativos"})

@login_required
def list_uploadrequest(request):
    uploads_requests = list(LocalUploadRequest.objects.all()) + list(RemoteUploadRequest.objects.all())
    if 'ajax' in request.POST:
        l = []
        for up in uploads_requests:
            d = {}
            d['pk'] = up.id
            # d['model'] = up.model
            d['fields'] = {}
            d['fields']['filename'] = up.volume.filename
            d['fields']['created_at'] = up.created_at.strftime("%d/%m/%Y %H:%M")
            d['fields']['attempts'] = up.attempts
            if up.last_attempt:
                d['fields']['last_attempt'] = up.last_attempt.strftime("%d/%m/%Y %H:%M")
            else:
                d['fields']['last_attempt'] = None
            d['fields']['friendly_rate'] = up.friendly_rate
            d['fields']['estimated_transfer_time'] = up.estimated_transfer_time
            d['fields']['finished_percent'] = up.finished_percent
            l.append(d)
        # response = serializers.serialize("json", uploads_requests)
        response = simplejson.dumps(l)
        return HttpResponse(response, mimetype="text/plain")
    return render_to_response(request, 
                              "list_downuploadrequest.html", 
                              {"object_list": uploads_requests,
                               "list_type": "Uploads",
                               "title": u"Uploads ativos"})

@login_required
def list_procedures(request):
    procedures = Procedure.objects.filter(id__gt=1, offsite_on=True)
    extra_content = {'procedures': procedures,
                     'title': u"Procedimentos com offsite ativo"}
    return render_to_response(request, "procedures_list.html", extra_content)
