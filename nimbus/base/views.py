# -*- coding: utf-8 -*-
# Create your views here.

import operator

import systeminfo

from django.contrib.auth.decorators import login_required

from nimbus.shared.views import render_to_response
from nimbus.bacula.models import Job

from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer


@login_required
def home(request):

    job_bytes = Job.get_bytes_from_last_jobs()
    job_files = Job.get_files_from_last_jobs()

    table1 = {}
    table1['title'] = u"Dados armazenados por dia"
    table1['area'] = "48%"
    table1['type'] = "area"
    table1['header'] = sorted(job_bytes)
    table1['lines'] = {
        "Bytes": map( operator.itemgetter(1), sorted(job_bytes.items())),
        "Arquivos" : map( operator.itemgetter(1), sorted(job_files.items()))}


    job_files = Job.get_files_from_last_jobs()
    table2 = {}
    table2['title'] = u"Quantidade de arquivos realizados backup"
    table2['area'] = "48%"
    table2['type'] = "area"
    table2['header'] = sorted(job_files)
    table2['lines'] = {
        "Bytes": map( operator.itemgetter(1), sorted(job_files.items())) }


    
    diskinfo = systeminfo.DiskInfo("/")
    diskusage = diskinfo.get_usage()
    diskfree = 100 - diskinfo.get_usage()


    table3 = {}
    table3['title'] = u"Ocupação do disco"
    table3['width'] = "48%"
    table3['type'] = "pie"
    table3['header'] = ["Gigabytes"]
    table3['lines'] = {
        "Disponível": [diskfree],
        "Ocupado": [diskusage]}


    memory = systeminfo.get_memory_usage()
    memory_free = 100 - memory

    
    table4 = {}
    table4['title'] = u"Uso da memória"
    table4['width'] = "48%"
    table4['type'] = "pie"
    table4['header'] = ["Gigabytes"]
    table4['lines'] = {
        "Disponível": [memory_free],
        "Ocupado": [memory]}


    cpu = systeminfo.get_cpu_usage()
    cpu_free = 100 - memory

    
    table5 = {}
    table5['title'] = u"Uso da CPU"
    table5['width'] = "48%"
    table5['type'] = "pie"
    table5['header'] = ["Clocks"]
    table5['lines'] = {
        "Disponível": [cpu_free],
        "Em uso": [cpu]}

    offsite_usage = 55 #TODO
    offsite_free = 45

    
    table6 = {}
    table6['title'] = u"Uso do Offsite"
    table6['width'] = "48%"
    table6['type'] = "pie"
    table6['header'] = ["GB"]
    table6['lines'] = {
        "Disponível": [offsite_free],
        "Em uso": [offsite_usage]}

   
    
    # Dados de content:
    # - type
    # - label
    # - date
    # - message
    


    last_jobs = Job.objects.all()\
                    .order_by('endtime').distinct()[:5]


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


    errors_jobs = Job.objects.filter(jobstatus__in=('e','E','f'))\
                    .order_by('endtime').distinct()[:5]


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


   
    backups_com_falhas = [{
        'title': u'Últimos backups executados',
        'content': last_procedures_content  }, {
        'title': u'Backups com falha',
        'content': errors_procedures_content   
    }]
    
      
    # extra_content = {'table1': table1, 'table2': table2}
    return render_to_response(request, "home.html", locals())




def historico(request):
    table1 = {}
    table1['title'] = u"CPU"
    table1['type'] = "line"
    table1['header'] = ["00:00", "00:05", "00:10", "00:15", "00:20", "00:25", "00:30", "00:35", "00:40"]
    table1['lines'] = {
        "Core 1": ["0.2", "0.3", "0.25", "0.25", "0.35", "0.21", "0.25", "0.35", "0.21"],
        "Core 2": ["0.1", "0.1", "0.1", "0.15", "0.15", "0.21", "0.15", "0.12", "0.07"],
        "Core 3": ["0.4", "0.14", "0.63", "0.11", "0.12", "0.15", "0.51", "0.1", "0.51"],
        "Core 4": ["0.14", "0.17", "0.05", "0.15", "0.31", "0.22", "0.14", "0.32", "0.17"]}

    table2 = {}
    table2['title'] = u"Memória"
    table2['type'] = "area"
    table2['header'] = ["00:00", "00:05", "00:10", "00:15", "00:20", "00:25", "00:30", "00:35", "00:40"]
    table2['lines'] = {
        "MB": ["145", "147", "150", "180", "124", "98", "99", "100", "112"]}

    extra_content = {'table1': table1, 'table2': table2}
    return render_to_response(request, "historico.html", extra_content)
