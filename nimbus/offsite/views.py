# -*- coding: utf-8 -*-

from urllib2 import URLError
from os.path import join
from datetime import datetime, timedelta
import simplejson

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _

from nimbus.libs import systemprocesses
from nimbus.offsite import managers
from nimbus.offsite.models import (LocalUploadRequest, 
                                   RemoteUploadRequest, 
                                   DownloadRequest)
from nimbus.procedures.models import Procedure
from nimbus.offsite.models import Offsite
from nimbus.offsite.queue_service import get_queue_progress_data
from nimbus.offsite.graphic import Graphics
from nimbus.shared import utils
# from nimbus.graphics.models import GraphicsManager, ResourceItemNotFound
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.offsite.forms import OffsiteForm
from nimbus.wizard.models import add_step
from nimbus.wizard.views import previous_step_url, next_step_url





@add_step()
def offsite(request):
    extra_context = {'wizard_title': _(u'3 of 5 - Offsite Configuration'),
                     'page_name': u'offsite',
                     'previous': previous_step_url('offsite')}
    return edit_singleton_model(request, "generic.html",
                                next_step_url('offsite'),
                                formclass = OffsiteForm,
                                extra_context = extra_context)






@login_required
def detail(request):
    offsite = Offsite.get_instance()
    uploads = list(LocalUploadRequest.objects.all()) + list(RemoteUploadRequest.objects.all())
    content = []
    for upload in uploads:
        content.append({'type' : 'ok',
                        'date' : upload.last_attempt or upload.created_at,
                        'label' : upload.volume.filename,
                        'message' : "%.2f MB" % utils.bytes_to_mb(upload.volume.size)
                       })
    transferencias_em_execucao = [{'title': _(u'Transfers in execution'),
                                   'content': content}]

    if offsite.active:
        graphic = Graphics()
        graph_block = graphic.data_to_template()[0]
    else:
        ocupacao_offsite = 0.0
        messages.error(request, _("Offsite disabled"))
    return render_to_response(request, "detail.html", locals())

@login_required
def edit(request):
    title = _(u'Edit offsite configuration')
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
                               "title": _(u"Active downloads")})

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
    uploads = get_queue_progress_data()
    upload_total = 0.0 # bytes
    upload_done = 0.0 # bytes
    current_speed = 0.0 # B/s
    for u in uploads:
        current_speed += u["speed"]
        upload_total += u["total"]
        upload_done += u["done"]
    next_start = 0
    for u in uploads:
        u['portion'] = 100.0 * (u['total']) / (upload_total)
        u['block_width'] = int((910 - (len(uploads) * 6)) * (u['portion'] / 100.0))
        if u['block_width'] < 1:
            u['block_width'] = 1
        if next_start == 0:
            u["estimate_start"] = u["added"]
        else:
            delta_from_now = datetime.now() + timedelta(seconds=int(next_start))
            u["estimate_start"] = delta_from_now.strftime("%H:%M:%S de %d/%m/%Y")
        u["done_percent"] = (float(u["done"]) / u["total"]) * 100.0
        if u["speed"]:
            u["eta"] = int((u["total"] - u["done"]) / (u["speed"]))
        elif current_speed:
            u["eta"] = int((u["total"] - u["done"]) / (current_speed))
        else:
            u["eta"] = 0
        next_start += u["eta"]
        if u["eta"]:
            u["eta_str"] = str(timedelta(seconds=int(u["eta"])))
            u["end_time"] = datetime.now() + timedelta(seconds=int(next_start))
            u["end_time_str"] = u["end_time"].strftime("%H:%M:%S de %d/%m/%Y")
        else:
            u["eta_str"] = _("Stopped")
            u["end_time"] = 0
            u["end_time_str"] = _("Stopped")
        u['speed'] = u['speed'] / 1024.0 # kB/s
        u['total'] = u['total'] / 1048576.0 # MB
        u['done'] = u['done'] / 1048576.0 # MB
    if current_speed:
        eta = (upload_total - upload_done) / current_speed # seconds
        eta_str = str(timedelta(seconds=int(eta)))
        end_time = datetime.now() + timedelta(seconds=int(eta))
        end_time_str = end_time.strftime("%H:%M:%S de %d/%m/%Y")
    else:
        eta = 0
        eta_str = _("Stopped")
        end_time = 0
        end_time_str = _("Stopped")
    return {"uploads": uploads,
            "upload_total": upload_total / 1048576.0, # MB
            "upload_done": upload_done / 1048576.0, # MB
            "current_speed": current_speed / 1024.0, # kB/s
            "eta_str": eta_str,
            "end_time_str": end_time_str}

@login_required
def upload_queue(request):
    data = upload_queue_status()
    # data = get_queue_progress_data()
    data["title"] = _(u"Active uploads")
    return render_to_response(request, 
                              "upload_queue.html", data)

@login_required
def upload_queue_data(request):
    data = upload_queue_status()
    for item in range(len(data['uploads'])):
        data['uploads'][item]['eta'] = None
        data['uploads'][item]['end_time'] = None

    json_data = simplejson.dumps(data)
    return HttpResponse(json_data)


@login_required
def list_procedures(request):
    procedures = Procedure.objects.filter(id__gt=1, offsite_on=True)
    extra_content = {'procedures': procedures,
                     'title': _(u"Procedures with offsite active")}
    return render_to_response(request, "procedures_list.html", extra_content)


@login_required
def list_offsite(request):
    procedures = Procedure.with_job_tasks('Offsite')
    last_jobs = Procedure.jobs_with_job_tasks('Offsite')
    extra_content = {'procedures': procedures,
                     'last_jobs' : last_jobs,
                     'title': _(u"Procedures with offsite active")}

    return render_to_response(request, "procedures_list.html", extra_content)


@login_required
def csv_data(request):
    g = Graphics()
    d = g.last_days(days=90)
    r = ["Date,Utilizado"]
    for i in d:
        r.append("%s,%s" % (i.timestamp.strftime("%Y/%m/%d %H:%M:%S"), float(i.used)/1073741824.0))
    return HttpResponse("\n".join(r))

