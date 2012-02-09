# -*- coding: utf-8 -*-

from urllib2 import URLError
from os.path import join
from datetime import datetime, timedelta
import simplejson

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nimbus.libs import systemprocesses
from nimbus.offsite import managers
from nimbus.offsite.models import (LocalUploadRequest, 
                                   RemoteUploadRequest, 
                                   DownloadRequest)
from nimbus.procedures.models import Procedure
from nimbus.offsite.models import Offsite
from nimbus.offsite.graphic import Graphics
from nimbus.shared import utils
# from nimbus.graphics.models import GraphicsManager, ResourceItemNotFound
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.offsite.forms import OffsiteForm
from nimbus.wizard.models import add_step
from nimbus.wizard.views import previous_step_url, next_step_url





@add_step()
def offsite(request):
    extra_context = {'wizard_title': u'3 de 5 - Configuração do Offsite',
                     'page_name': u'offsite',
                     'previous': previous_step_url('offsite')}
    return edit_singleton_model(request, "generic.html",
                                next_step_url('offsite'),
                                formclass = OffsiteForm,
                                extra_context = extra_context)






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
        graphic = Graphics()
        graph_block = graphic.data_to_template()[0]
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

# WORKAROUND enquanto a central não informa o host do servidor de storage
def self_auth(request):
    return HttpResponse('{"status":1,"accesskey":{"id":"WKy3rMzOWPouVOxK1p3Ar1C2uRBwa2FBXnCw","secret":"OqB5HIRx7yEKBonz6lQI8jbN1Qg3Mguf1g5mw"},"quota":"10000", "host": "192.168.51.6"}')
    # return HttpResponse('{"status":1,"accesskey":{"id":"AKIAJB5RPEBFQLFOWMXQ","secret":"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"},"quota":"10000"}')


@login_required
def select_storage(request):
    return render_to_response(request, 
                              "select_storage.html",
                              {"devices" : managers.list_disk_labels()})

def copy_files_worker(storage):
    archive_devices = managers.find_archive_devices()
    for arc_dev in archive_devices:
        dest = join("/media" , storage)
        manager = managers.LocalManager(origin=arc_dev, destination=dest)
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

def upload_queue_status():
    uploads = [{"name": "Upload X",
                "id": 0,
                "total": 150,
                "done": 43,
                "speed": 130.0,
                "added": "03:15:09 de 08/02/2012",
                "current_file": "procedure_01923019872301873"},
               {"name": "Upload Y",
                "id": 1,
                "total": 150,
                "done": 12,
                "speed": 0.0,
                "added": "04:15:09 de 08/02/2012",
                "current_file": "procedure_8273698264397627983"},
               {"name": "Upload Z",
                "id": 2,
                "total": 300,
                "done": 10,
                "speed": 0.0,
                "added": "05:15:09 de 08/02/2012",
                "current_file": "procedure_287369827347263784234"},
                {"name": "Upload U",
                 "id": 3,
                 "total": 150,
                 "done": 0,
                 "speed": 0.0,
                 "added": "06:15:09 de 08/02/2012",
                 "current_file": "procedure_2837649782970823"},
                 {"name": "Upload X",
                 "id": 4,
                 "total": 500,
                 "done": 0,
                 "speed": 130.0,
                 "added": "03:15:09 de 08/02/2012",
                 "current_file": "procedure_01923019872301873"},
                {"name": "Upload Y",
                 "id": 5,
                 "total": 250,
                 "done": 0,
                 "speed": 0.0,
                 "added": "04:15:09 de 08/02/2012",
                 "current_file": "procedure_8273698264397627983"},
                {"name": "Upload Z",
                 "id": 6,
                 "total": 330,
                 "done": 0,
                 "speed": 0.0,
                 "added": "05:15:09 de 08/02/2012",
                 "current_file": "procedure_287369827347263784234"},
                 {"name": "Upload U",
                  "id": 7,
                  "total": 150,
                  "done": 0,
                  "speed": 0.0,
                  "added": "06:15:09 de 08/02/2012",
                  "current_file": "procedure_2837649782970823"}]
    upload_total = 0.0 # MB
    upload_done = 0.0 # MB
    current_speed = 0.0 # kB/s
    for u in uploads:
        current_speed += u["speed"]
        upload_total += u["total"]
        upload_done += u["done"]
    next_start = 0
    for u in uploads:
        u['portion'] = 100.0 * (u['total'] - u['done']) / (upload_total - upload_done)
        if next_start == 0:
            u["estimate_start"] = u["added"]
        else:
            delta_from_now = datetime.now() + timedelta(seconds=int(next_start))
            u["estimate_start"] = delta_from_now.strftime("%H:%M:%S de %d/%m/%Y")
        u["done_percent"] = (u["done"] / u["total"]) * 100.0
        if u["speed"]:
            u["eta"] = int((u["total"] - u["done"]) / (u["speed"] / 1024))
        elif current_speed:
            u["eta"] = int((u["total"] - u["done"]) / (current_speed / 1024))
        else:
            u["eta"] = 0
        next_start += u["eta"]
        if u["eta"]:
            u["eta_str"] = str(timedelta(seconds=int(u["eta"])))
            u["end_time"] = datetime.now() + timedelta(seconds=int(next_start))
            u["end_time_str"] = u["end_time"].strftime("%H:%M:%S de %d/%m/%Y")
        else:
            u["eta_str"] = "Parado"
            u["end_time"] = 0
            u["end_time_str"] = "Parado"
    if current_speed:
        eta = (upload_total - upload_done) / (current_speed / 1024.0) # seconds
        eta_str = str(timedelta(seconds=int(eta)))
        end_time = datetime.now() + timedelta(seconds=int(eta))
        end_time_str = end_time.strftime("%H:%M:%S de %d/%m/%Y")
    else:
        eta = 0
        eta_str = "Parado"
        end_time = 0
        end_time_str = "Parado"
    return {"uploads": uploads,
            "upload_total": upload_total,
            "upload_done": upload_done,
            "current_speed": current_speed,
            "eta_str": eta_str,
            "end_time_str": end_time_str}

@login_required
def upload_queue(request):
    data = upload_queue_status()
    data["title"] = u"Uploads ativos"
    return render_to_response(request, 
                              "upload_queue.html", data)

@login_required
def list_procedures(request):
    procedures = Procedure.objects.filter(id__gt=1, offsite_on=True)
    extra_content = {'procedures': procedures,
                     'title': u"Procedimentos com offsite ativo"}
    return render_to_response(request, "procedures_list.html", extra_content)


@login_required
def list_offsite(request):
    procedures = Procedure.with_job_tasks('Offsite')
    last_jobs = Procedure.jobs_with_job_tasks('Offsite')
    extra_content = {'procedures': procedures,
                     'last_jobs' : last_jobs,
                     'title': u"Procedimentos com offsite ativo"}

    return render_to_response(request, "procedures_list.html", extra_content)



