# -*- coding: utf-8 -*-
# Create your views here.


import os
import simplejson
import xmlrpclib
from glob import glob
from datetime import datetime


from django.conf import settings
from django.core import serializers
from django.http import HttpResponse 
from django.shortcuts import redirect
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from nimbus.computers.models import Computer
from nimbus.procedures.models import Procedure
from nimbus.shared.views import render_to_response
from nimbus.libs.bacula import Bacula





@login_required
def view(request, object_id=None):
    computer = None

    if object_id:
        try:
            computer = Computer.objects.get(id=object_id, active=True)
        except Computer.DoesNotExist, error:
            return redirect('nimbus.restore.views.view')

    #computers = Computer.objects.filter(active=True,id__gt=1)
    computers = Computer.objects.filter(active=True)
    
    extra_content = {
        'computer': computer,
        'computers': computers,
        'title': u"Restauração de arquivos"
    }
    return render_to_response(request, "restore_list.html", extra_content)



@login_required
def restore_files(request):
    """docstring for restore_files"""
    
    ## Parametros:
    # computer_id
    # procedure_id
    # job_id
    # destino
    # data_inicio
    # data_fim
    # path (lista)
    
    if request.method == "POST":

        computer = Computer.objects.get(id=request.POST["computer_id"])
        jobid = int(request.POST["job_id"])
        target = request.POST["path_restore"]
        files = request.POST.getlist("path")

        bacula = Bacula()
        bacula.run_restore( computer.bacula_name, jobid, target, files)  

        messages.success(request, "Recuperação iniciada com sucesso")
    
        return redirect('nimbus.restore.views.view')



@login_required
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
    


@login_required
def get_jobs(request, procedure_id, data_inicio, data_fim):
    """Return all jobs that match computer, procedure and date."""
    # TODO: Get the jobs...
    # jobs = [{"name": "Job1 - 10 Aug 2010", "id": "59"},
    #         {"name": "Job2 - 11 Aug 2010", "id": "60"},
    #         {"name": "Job3 - 12 Aug 2010", "id": "61"},
    #         {"name": "Job3 - 12 Aug 2010", "id": "37"}]

    # response = serializers.serialize("json", jobs)
    #print "jobs" * 200
    #print procedure_id

    data_inicio = "%s 00:00:00" % data_inicio
    data_inicio = datetime.strptime(data_inicio, '%d-%m-%Y %H:%M:%S')

    data_fim = "%s 23:59:59" % data_fim
    data_fim = datetime.strptime(data_fim, '%d-%m-%Y %H:%M:%S')

    procedure = Procedure.objects.get(id=procedure_id)
    jobs = procedure.get_backup_jobs_between(data_inicio, data_fim)

    # response = simplejson.dumps(jobs)
    response = serializers.serialize("json", jobs, fields=("realendtime", "jobfiles", "name"))
    return HttpResponse(response, mimetype="text/plain")



@login_required
def get_tree(request):
    path = request.POST['path']
    job_id = request.POST['job_id']
    
    files = Procedure.list_files(job_id, path)

    response = simplejson.dumps(files)
    return HttpResponse(response, mimetype="text/plain")


@login_required
def get_client_tree(request):

    if request.method == "POST":

        path = request.POST['path']
        computer_id = request.POST['computer_id']

        computer = Computer.objects.get(id=computer_id)

        url = "http://%s:%d" % (computer.address, settings.NIMBUS_CLIENT_PORT)
        proxy = xmlrpclib.ServerProxy(url)
        files = proxy.list_dir(path)
        files.sort()
        response = simplejson.dumps(files)
        return HttpResponse(response, mimetype="text/plain")

           


def get_tree_search_file(request):
    pattern = request.POST['pattern']
    job_id = request.POST['job_id']

    files = Procedure.search_files(job_id, pattern)

    response = simplejson.dumps(files)
    return HttpResponse(response, mimetype="text/plain")


# def view(request, object_id):
#     computers = Computer.objects.get(id=object_id)
#     extra_content = {
#         'computer': computers,
#         'title': u"Visualizar computador"
#     }
#     return render_to_response(request, "computers_view.html", extra_content)
