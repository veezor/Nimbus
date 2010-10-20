# -*- coding: utf-8 -*-

from os.path import join
from threading import Thread

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core import serializers

from nimbus.libs import offsite
from nimbus.offsite.models import UploadRequest, DownloadRequest
from nimbus.procedures.models import Procedure
from nimbus.offsite.models import Offsite
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.offsite.forms import OffsiteForm


def detail(request):
    offsite = Offsite.objects.all()[0]
    transferencias_em_execucao = {
        'title': u'Transferências em execução',
        'content': [
            {'type': 'ok', 'label': 'Servidor Web', 'date': '20/09/2010 10:25', 'message': '20 MB'},
            {'type': 'warn', 'label': 'Sala A - Comp 1', 'date': '20/09/2010 10:15', 'message': '3 MB'},
        ]
    }
    return render_to_response(request, "detail.html", locals())



def edit(request):
    title = u'Editar configurações do offsite'
    
    return edit_singleton_model( request, "offsite_edit.html", 
                                 "nimbus.offsite.views.detail",
                                 formclass = OffsiteForm,
                                 extra_context = locals() )


@login_required
def select_storage(request):
    return render_to_response( request, 
                               "select_storage.html",
                               {"devices" : offsite.list_disk_labels() })





def worker_thread(storage):
    archive_devices = offsite.find_archive_devices()
    for arc_dev in archive_devices:
        dest = join( "/media" , storage )
        manager = offsite.LocalManager(origin=arc_dev, 
                                       destination=dest)
        manager.upload_all_volumes()


@login_required
def copy_files_to_storage(request):

    if request.method == "POST":

        device = request.POST.get("device")

        if not device:
            raise Http404()

        thread = Thread(target=worker_thread, args=(device,))
        thread.start()

        return redirect('nimbus.offsite.views.list_uploadrequest')
    else:
        return redirect('nimbus.offsite.views.list_uploadrequest')


@login_required
def list_downloadrequest(request):
    from datetime import datetime
    import simplejson
    downloads_requests = DownloadRequest.objects.all()
    
    if 'ajax' in request.POST:
        l = []
        for down in downloads_requests:
            d = {}
            d['pk'] = down.id
            # d['model'] = down.model
            d['fields'] = {}
            d['fields']['filename'] = down.volume.filename
            d['fields']['created_at'] = datetime.strftime(down.created_at, "%d/%m/%Y %H:%M")
            d['fields']['attempts'] = down.attempts
            d['fields']['last_attempt'] = down.last_attempt
            d['fields']['friendly_rate'] = down.friendly_rate
            d['fields']['estimated_transfer_time'] = down.estimated_transfer_time
            d['fields']['finished_percent'] = down.finished_percent
            l.append(d)
        # response = serializers.serialize("json", downloads_requests)
        response = simplejson.dumps(l)
        return HttpResponse(response, mimetype="text/plain")
        
    return render_to_response( request, 
                               "list_downuploadrequest.html", 
                               {"object_list": downloads_requests,
                                "list_type": "Downloads",
                                "title": u"Downloads ativos"})


@login_required
def list_uploadrequest(request):
    from datetime import datetime
    import simplejson
    uploads_requests = UploadRequest.objects.all()
    
    if 'ajax' in request.POST:
        l = []
        for up in uploads_requests:
            d = {}
            d['pk'] = up.id
            # d['model'] = up.model
            d['fields'] = {}
            d['fields']['filename'] = up.volume.filename
            d['fields']['created_at'] = datetime.strftime(up.created_at, "%d/%m/%Y %H:%M")
            d['fields']['attempts'] = up.attempts
            d['fields']['last_attempt'] = up.last_attempt
            d['fields']['friendly_rate'] = up.friendly_rate
            d['fields']['estimated_transfer_time'] = up.estimated_transfer_time
            d['fields']['finished_percent'] = up.finished_percent
            l.append(d)
        # response = serializers.serialize("json", uploads_requests)
        response = simplejson.dumps(l)
        return HttpResponse(response, mimetype="text/plain")
    
    return render_to_response( request, 
                              "list_downuploadrequest.html", 
                              {"object_list": uploads_requests,
                               "list_type": "Uploads",
                               "title": u"Uploads ativos"})


@login_required
def list_procedures(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos com offsite ativo"
    }
    return render_to_response(request, "procedures_list.html", extra_content)

