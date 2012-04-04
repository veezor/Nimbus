#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import systeminfo

from django.http import Http404, HttpResponse
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from nimbus.storages.models import Storage
from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.libs.bacula import call_reload_baculadir
from nimbus.shared.forms import form
from nimbus.bacula.models import Job
from nimbus.storages.graphic import Graphics

@login_required
def new(request):

    if request.method == "POST":
        try:
            password = request.POST['password']

            name = request.META.get('REMOTE_HOST')
            if not name:
                name = _(u"Automatically added")

            storage =  Storage(name = name,
                                address = request.META['REMOTE_ADDR'],
                                password= request.POST['password'],
                                description=_("Storage automatically identified"))
            storage.save()

            return HttpResponse(status=200)
        except (KeyError, IntegrityError), e:
            return HttpResponse(status=400)



@login_required
def add(request):
    title = _(u"Add Storage")
    storages = Storage.objects.filter(active=False)
    return render_to_response(request, "storages_add.html", locals())



@login_required
def edit(request, object_id):
    extra_context = {'title': _(u"Edit Storage")}
    r =  create_update.update_object( request,
                                      object_id = object_id,
                                      model = Storage,
                                      form_class = form(Storage),
                                      template_name = "storages_edit.html",
                                      extra_context = extra_context,
                                      post_save_redirect = "/storages/list")
    call_reload_baculadir()
    return r


@login_required
def list(request):
    d = {
        "storages" : Storage.objects.filter(active=True),
        "title": _(u"Storages")
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
                'message' : _(u'Computer : %s') % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


    backups_em_execucao = [{
        'title': _(u'Backups in progress'),
        'content': running_procedures_content
    }]

    diskinfo = systeminfo.DiskInfo("/bacula")
    try:
        diskusage = diskinfo.get_usage()
    except OSError, error:
        messages.error(request, _(u"Partition /bacula not found"))
        diskusage = 0


    d = {
        "storage" : storage,
        "title": _(u"Storage"),
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
        "title": _(u'Computers of Storage "%s"') % storage.name
    }
    return render_to_response(request, "computers_list.html", d)


@login_required
def activate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = True
    storage.save()

    messages.success(request, _(u'Storage enabled.'))
    return redirect('/storages/list')


@login_required
def deactivate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = False
    storage.save()

    return redirect('/storages/list')

@login_required
def csv_data(request):
    g = Graphics()
    d = g.last_days(days=90)
    r = ["Date,Utilizado"]
    for i in d:
        r.append("%s,%s" % (i.timestamp.strftime("%Y/%m/%d %H:%M:%S"), float(i.used)/1073741824.0))
    return HttpResponse("\n".join(r))
    
    
    
    
    
