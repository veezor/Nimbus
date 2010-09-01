# -*- coding: utf-8 -*-
# Create your views here.

import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.core import serializers

from nimbus.computers.models import Computer
from nimbus.procedures.models import Procedure
from nimbus.shared.views import render_to_response

from django.http import HttpResponse, HttpResponseRedirect


def view(request, object_id=None):
    if object_id:
        computer = Computer.objects.get(id=object_id)
    else:
        computer = None
    computers = Computer.objects.all()
    extra_content = {
        'computer': computer,
        'computers': computers,
        'title': u"Restauração de arquivos"
    }
    return render_to_response(request, "restore_list.html", extra_content)



def get_procedures(request, object_id=None):
    if not object_id:
        message = {'error': 'Erro ao tentar selecionar o computador.'}
        response = simplejson.dumps(message)
        return HttpResponse(response, mimetype="text/plain")
    
    procedures = Procedure.objects.filter(computer=object_id)
    # computer = Computer.objects.get(id=object_id)
    if not procedures.count():
        message = {'error': 'Erro ao tentar selecionar o computador.'}
        response = simplejson.dumps(message)
        return HttpResponse(response, mimetype="text/plain")
    
    # message = {'error': 'Erro ao tentar selecionar o computador.'}
    # response = simplejson.dumps(computer.procedure_set.all())
    response = serializers.serialize("json", procedures)
    return HttpResponse(response, mimetype="text/plain")
    


def get_jobs(request, computer_id=None, procedure_id=None, data_inicio=None, data_fim=None):
    """Return all jobs that match computer, procedure and date."""
    # TODO: Get the jobs...
    jobs = [{"name": "Job1 - 10 Aug 2010", "id": "1"},
            {"name": "Job2 - 11 Aug 2010", "id": "2"},
            {"name": "Job3 - 12 Aug 2010", "id": "3"}]
    
    # response = serializers.serialize("json", jobs)
    response = simplejson.dumps(jobs)
    return HttpResponse(response, mimetype="text/plain")



def get_tree(request):
    path = request.POST['path']
    
    if path == '/':
        files = [
            path + 'var/',
            path + 'mach_kernel'
        ]
    
    if path == '/var/':
        files = [
            path + 'tmp/',
            path + 'abc/',
            path + 'duque/',
        ]
    
    if path == '/var/tmp/':
        files = [
            path + 'a.sql',
            path + 'b.txt',
            path + 'c.py',
        ]
    
    if path == '/var/abc/':
        files = []
    
    if path == '/var/duque/':
        files = [
            path + 'o.out'
        ]
    
    # files = [
    #     '/var/',
    #     '/var/tmp/',
    #     '/var/tmp/a.sql',
    #     '/var/tmp/b.txt',
    #     '/var/tmp/c.py',
    #     '/var/abc/',
    #     '/var/duque/',
    #     '/var/duque/o.out'
    #     '/etc/',
    #     '/etc/nimbus/',
    #     '/etc/nimbus/manager.py',
    #     '/etc/nimbus/teste.py',
    # ]
    response = simplejson.dumps(files)
    return HttpResponse(response, mimetype="text/plain")

# def view(request, object_id):
#     computers = Computer.objects.get(id=object_id)
#     extra_content = {
#         'computer': computers,
#         'title': u"Visualizar computador"
#     }
#     return render_to_response(request, "computers_view.html", extra_content)
