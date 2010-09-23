# -*- coding: utf-8 -*-

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.computers.models import Computer, ComputerGroup
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form




def add(request):
    extra_context = {'title': u"Adicionar computador"}
    return create_update.create_object( request, 
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")



def edit(request, object_id):
    extra_context = {'title': u"Editar computador"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")



def delete(request):
    pass

def list(request):
    computers = Computer.objects.all()
    extra_content = {
        'computers': computers,
        'title': u"Computadores"
    }
    return render_to_response(request, "computers_list.html", extra_content)


def view(request, object_id):
    computers = Computer.objects.get(id=object_id)
    extra_content = {
        'computer': computers,
        'title': u"Visualizar computador"
    }
    return render_to_response(request, "computers_view.html", extra_content)


def group_add(request):
    if 'name' in request.POST:
        name = request.POST['name']
    else:
        name = u'Criação'
    try:
        group = ComputerGroup(name=name)
        group.save()
    except Exception, e:
        print e
        response = dict(message='error')
    else:
        response = dict(message='success')
    return HttpResponse(simplejson.dumps(response))


def group_list(request):
    ajax = request.POST['ajax']
        
    if not ajax:
        return redirect('/')

    groups = ComputerGroup.objects.all()
    
    response = serializers.serialize("json", groups)
    return HttpResponse(response, mimetype="text/plain")


def activate(request, object_id):
    computer = Computer.objects.get(id=object_id)
    computer.active = 1
    computer.save()

    # messages.success(u'Armazenamento ativado com sucesso.')
    return redirect('/computers/list')


def deactivate(request, object_id):
    computer = Computer.objects.get(id=object_id)
    computer.active = 0
    computer.save()

    # messages.success(u'Armazenamento ativado com sucesso.')
    return redirect('/computers/list')

