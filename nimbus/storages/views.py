#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import simplejson

import systeminfo

from django.http import HttpResponse
from django.views.generic import create_update
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nimbus.config.models import Config
from nimbus.storages.models import Storage
from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form
from nimbus.bacula.models import Job

@login_required
def new(request):

    if request.method == "POST":
        try:

            config = Config.get_instance()

            name = request.POST['name']
            password = request.POST['password']
            address = request.META['REMOTE_ADDR']
            director_name = config.director_name


            if Storage.objects.filter(address=address).count():
                return HttpResponse(status=400)


            storage =  Storage(name=name,
                                address=address,
                                password=password,
                                description="Armazenamento identificado automaticamente")
            storage.save()
            json_response = simplejson.dumps(dict(token=storage.auth_token,
                                                  director_name=director_name))
            response = HttpResponse(json_response, mimetype="application/json", status=200)
            response['Content-Disposition'] = 'attachment; filename="result.json"'
            return response
        except (KeyError, IntegrityError), e:
            return HttpResponse(status=400)



@login_required
def add(request):
    title = u"Adicionar armazenamento"
    storages = Storage.objects.filter(active=False)
    return render_to_response(request, "storages_add.html", locals())



@login_required
def edit(request, object_id):
    extra_context = {'title': u"Editar armazenamento"}
    return create_update.update_object( request,
                                        object_id = object_id,
                                        model = Storage,
                                        form_class = form(Storage),
                                        template_name = "storages_edit.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/storages/list")


@login_required
def list(request):
    d = {
        "storages" : Storage.objects.filter(active=True),
        "title": u"Armazenamento"
    }

    return render_to_response(request, "storages_list.html", d)

    # extra_content = {"object_list": Device.objects.all()}
    # return render_to_response(request, "list_storages.html", extra_content)


@login_required
def view(request, object_id):
    storage = Storage.objects.get(id=object_id)

    running_status = ('R','p','j','c','d','s','M','m','s','F','B')
    running_jobs = Job.objects.filter( jobstatus__in=running_status)\
                                 .order_by('-starttime').distinct()[:5]


    running_procedures_content = []
    try:
        for job in running_jobs:
            running_procedures_content.append({
                'type' : 'ok',
                'label' : job.procedure.name,
                'date' : job.starttime,
                'tooltip' : job.status_message,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


    backups_em_execucao = [{
        'title': u'Backups em Execução',
        'content': running_procedures_content
    }]

    diskinfo = systeminfo.DiskInfo("/bacula")
    try:
        diskusage = diskinfo.get_usage()
    except OSError, error:
        messages.error(request, "Partição /bacula não encontrada")
        diskusage = 0


    d = {
        "storage" : storage,
        "title": u"Armazenamento",
        "backups_em_execucao": backups_em_execucao,
        "espaco_em_disco": diskusage
    }

    return render_to_response(request, "storages_view.html", d)


@login_required
def view_computer(request, object_id):
    storage = Storage.objects.get(id=object_id)
    computers = Computer.objects.filter(procedure__profile__storage=storage)
    d = {
        "storage" : storage,
        "computers" : computers,
        "title": u'Computadores do armazenamento "%s"' % storage.name
    }
    return render_to_response(request, "computers_list.html", d)


@login_required
def activate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = True
    storage.save()

    messages.success(request, u'Armazenamento ativado com sucesso.')
    return redirect('/storages/list')


@login_required
def deactivate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = False
    storage.save()

    return redirect('/storages/list')
