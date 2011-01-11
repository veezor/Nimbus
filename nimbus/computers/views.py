# -*- coding: utf-8 -*-

import simplejson
import socket
import xmlrpclib

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.contrib import messages
from django.db import IntegrityError
from django.conf import settings

from nimbus.computers.models import Computer, ComputerGroup
from nimbus.bacula.models import Job
from nimbus.shared.views import render_to_response
from nimbus.shared import enums
from nimbus.shared.forms import form
from nimbus.libs.template import render_to_string




@login_required
def new(request):

    if request.method == "POST":
        try:
            os = request.POST['os']
            if os not in enums.operating_systems:
                return HttpResponse(status=400)
            
            name = request.META.get('REMOTE_HOST')
            if not name:
                name = u"Adicionado automaticamente"

            computer = Computer(name = name,
                                 address = request.META['REMOTE_ADDR'],
                                 operation_system=os,
                                 description="Computador identificado automaticamente")
            computer.save()

            return HttpResponse(status=200)
        except (KeyError, IntegrityError), e:
            return HttpResponse(status=400)




@login_required
def add(request):
    title = u"Adicionar computador"
    computers = Computer.objects.filter(active=False)
    
    return render_to_response(request, "computers_add.html", locals())



@login_required
def edit(request, object_id):
    extra_context = {'title': u"Editar computador"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")


@login_required
def edit_no_active(request, object_id):
    extra_context = {'title': u"Editar computador"}
    messages.warning(request, u"O computador ainda não foi ativado.")
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = reverse("nimbus.computers.views.add"))



@login_required
def delete(request, object_id):
    if request.method == "POST":
        computer = Computer.objects.get(id=object_id)
        computer.delete()
        messages.success(request, u"Computador removido com sucesso.")
        return redirect('nimbus.computers.views.list')
    else:
        computer = Computer.objects.get(id=object_id)
        remove_name = computer.name
        return render_to_response(request, 'remove.html', locals())



@login_required
def list(request):
    computers = Computer.objects.filter(active=True)
    extra_content = {
        'computers': computers,
        'title': u"Computadores"
    }
    return render_to_response(request, "computers_list.html", extra_content)


@login_required
def view(request, object_id):
    computer = Computer.objects.get(id=object_id)

    running_status = ('R','p','j','c','d','s','M','m','s','F','B')
    running_jobs = Job.objects.filter( jobstatus__in=running_status,
                                       client__name=computer.bacula_name)\
                                            .order_by('-starttime').distinct()[:5]


    running_procedures_content = []
    try:
        for job in running_jobs:
            running_procedures_content.append({
                'type' : 'ok',
                'label' : job.procedure.name,
                'date' : job.starttime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass



    last_jobs = Job.objects.filter(client__name=computer.bacula_name)\
                    .order_by('-endtime').distinct()[:5]


    last_procedures_content = []
    try:
        for job in last_jobs:
            last_procedures_content.append({
                'type' : job.status_friendly,
                'label' : job.procedure.name,
                'date' : job.endtime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


    errors_jobs = Job.objects.filter(jobstatus__in=('e','E','f'),
                                     client__name=computer.bacula_name)\
                                    .order_by('-endtime').distinct()[:5]


    errors_procedures_content = []
    try:
        for job in errors_jobs:
            errors_procedures_content.append({
                'type' : job.status_friendly,
                'label' : job.procedure.name,
                'date' : job.endtime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


  
    backups_em_execucao = [{
        'title': u'Backups em Execução',
        'content': running_procedures_content 
    }]


    backups_com_falhas = [{
        'title': u'Últimos backups executados',
        'content': last_procedures_content  }, {
        'title': u'Backups com falha',
        'content': errors_procedures_content   
    }]
 
    
    extra_content = {
        'computer': computer,
        'title': u"Visualizar computador",
        'backups_em_execucao': backups_em_execucao,
        'backups_executados_e_com_falhas': backups_com_falhas,
    }
    return render_to_response(request, "computers_view.html", extra_content)


@login_required
def group_add(request):
    if 'name' in request.POST:
        name = request.POST['name']
    else:
        name = u'Criação'
    try:
        group = ComputerGroup(name=name)
        group.save()
    except Exception, e:
        response = dict(message='error')
    else:
        response = dict(message='success')
    return HttpResponse(simplejson.dumps(response))


@login_required
def group_list(request):
    ajax = request.POST['ajax']
        
    if not ajax:
        return redirect('/')

    groups = ComputerGroup.objects.all()
    
    response = serializers.serialize("json", groups)
    return HttpResponse(response, mimetype="text/plain")


@login_required
def activate(request, object_id):
    try:
        computer = Computer.objects.get(id=object_id)
        computer.activate()

        messages.success(request, u'Computador ativado com sucesso.')
        return redirect('nimbus.computers.views.list')
    except (socket.error, xmlrpclib.Fault), error:
        messages.error(request, u'Impossível ativar computador, verifique a conexão')


@login_required
def deactivate(request, object_id):
    computer = Computer.objects.get(id=object_id)
    computer.active = 0
    computer.save()

    # messages.success(u'Armazenamento ativado com sucesso.')
    return redirect('/computers/list')

