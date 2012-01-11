# -*- coding: utf-8 -*-
# Create your views here.


import os
import simplejson
import xmlrpclib
from glob import glob
from datetime import datetime, timedelta


from django.conf import settings
from django.core import serializers
from django.http import HttpResponse 
from django.shortcuts import redirect
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from nimbus.bacula.models import Job
from nimbus.computers.models import Computer
from nimbus.procedures.models import Procedure
from nimbus.shared.views import render_to_response
from nimbus.libs.bacula import Bacula

@login_required
def step1(request):
    """Selecionar o computador"""
    computers = Computer.objects.filter(active=True,id__gt=1)
    extra_content = {
        'computers': computers,
        'title': u"Restauração de arquivos"
    }
    return render_to_response(request, "step1.html", extra_content)

@login_required
def step2(request):
    """Selecionar do procedure"""
    if (request.method == "POST") or (request.method == "GET"):
        if (request.method == "POST"):
            data = request.POST
        elif (request.method == "GET"):
            if request.GET.has_key("computer_id") == False:
                return redirect('nimbus.restore.views.step1')
            else:
                data = request.GET
        computer = Computer.objects.get(id=data["computer_id"])
        extra_content = {
            'computer': computer,
            'title': u"Restauração de arquivos"
        }
        return render_to_response(request, "step2.html", extra_content)
    else:
        return redirect('nimbus.restore.views.step1')

@login_required
def step3(request):
    """Selecionar o JOB"""
    if request.method == "POST":
        data = request.POST
        computer = Computer.objects.get(id=data["computer_id"])
        procedure = Procedure.objects.get(id=data["procedure_id"])
        if data.has_key("start_date") and data.has_key("end_date"):
            start_date = datetime.strptime(data["start_date"], "%d/%m/%Y")
            end_date = datetime.strptime(data["end_date"] + " 23:59:59", "%d/%m/%Y %H:%M:%S")
            jobs = procedure.get_backup_jobs_between(start_date, end_date)
        else:
            end_date = datetime.now()
            start_date = datetime.today() - timedelta(30)
            jobs = procedure.get_backup_jobs_between(start_date, end_date)
            # jobs = procedure.all_my_good_jobs
        extra_content = {
            'computer': computer,
            'procedure': procedure,
            'jobs': jobs,
            'start_date': start_date.strftime("%d/%m/%Y"),
            'end_date': end_date.strftime("%d/%m/%Y"),
            'title': u"Restauração de arquivos"
        }
        return render_to_response(request, "step3.html", extra_content)
    else:
        return redirect('nimbus.restore.views.step1')

@login_required
def step4(request):
    """Escolher os arquivos"""
    if request.method == "POST":
        data = request.POST
        computer = Computer.objects.get(id=data["computer_id"])
        procedure = Procedure.objects.get(id=data["procedure_id"])
        job = Job.objects.get(jobid=data["job_id"])
        extra_content = {
            'computer': computer,
            'procedure': procedure,
            'job': job,
            'title': u"Restauração de arquivos"
        }
        if data.has_key('paths'):
            paths = data.getlist("paths")
            extra_content['paths'] = paths
        return render_to_response(request, "step4.html", extra_content)
    else:
        return redirect('nimbus.restore.views.step1')

@login_required
def step5(request):
    """Definir o destino dos arquivos"""
    if request.method == "POST":
        data = request.POST
        computer = Computer.objects.get(id=data["computer_id"])
        procedure = Procedure.objects.get(id=data["procedure_id"])
        job = Job.objects.get(jobid=data["job_id"])
        files = data.getlist("paths")
        files = list(set(files))
        files.sort()
        extra_content = {
            'computer': computer,
            'procedure': procedure,
            'job': job,
            'files': files,
            'title': u"Restauração de arquivos"
        }
        return render_to_response(request, "step5.html", extra_content)
    else:
        return redirect('nimbus.restore.views.step1')

@login_required
def step6(request):
    """Resumo e restore"""
    if request.method == "POST":
        data = request.POST
        computer = Computer.objects.get(id=data["computer_id"])
        procedure = Procedure.objects.get(id=data["procedure_id"])
        job = Job.objects.get(jobid=data["job_id"])
        files = data.getlist("paths")
        destination = data.get("destination_restore_path", "")
        extra_content = {
            'computer': computer,
            'procedure': procedure,
            'job': job,
            'files': files,
            'destination': destination,
            'title': u"Restauração de arquivos"
        }
        return render_to_response(request, "step6.html", extra_content)
    else:
        return redirect('nimbus.restore.views.step1')


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
        target = request.POST["destination"]
        files = request.POST.getlist("paths")
        bacula = Bacula()
        print request.POST
        bacula.run_restore(computer.bacula_name, jobid, target, files)
        messages.success(request, "Recuperação iniciada com sucesso")    
        return redirect('/procedures/list/')

@login_required
def get_tree(request):
    path = request.POST['path']
    job_id = request.POST['job_id']
    computer_id = request.POST['computer_id']
    computer = Computer.objects.get(id=computer_id)
    
    files = Procedure.list_files(job_id, computer, path)
    # teste que força o retorno da lista de arquivos
    #files = ["/home/lucas/arquivo1.txt", "/home/lucas/arquivo2.txt"];
    response = simplejson.dumps(files)
    return HttpResponse(response, mimetype="text/plain")

@login_required
def get_tree_search_file(request):
    pattern = request.POST['pattern']
    job_id = request.POST['job_id']

    files = Procedure.search_files(job_id, pattern)

    response = simplejson.dumps(files)
    return HttpResponse(response, mimetype="text/plain")
