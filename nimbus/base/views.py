# -*- coding: utf-8 -*-
# Create your views here.

import operator

import systeminfo

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nimbus.shared import utils
from nimbus.shared.views import render_to_response
from nimbus.bacula.models import Job
from nimbus.libs import graphsdata

from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer


@login_required
def home(request):

    job_bytes = Job.get_bytes_from_last_jobs()



    table1 = {}
    table1['title'] = u"Quantidade de megabytes realizados backup"
    table1['width'] = "100%"
    table1['type'] = "bar"
    table1['cid'] = "chart1"
    table1['header'] = [ d.strftime("%d/%m/%y") for d in sorted(job_bytes)  ]
    table1['lines'] = {
        "Mega bytes": utils.ordered_dict_value_to_formatted_float(job_bytes)
    }

    job_files = Job.get_files_from_last_jobs()
    table2 = {}
    table2['title'] = u"Quantidade de arquivos realizados backup"
    table2['width'] = "100%"
    table2['type'] = "bar"
    table2['cid'] = "chart2"
    table2['header'] = [ d.strftime("%d/%m/%y") for d in sorted(job_files) ]
    table2['lines'] = {
        "Arquivos": utils.ordered_dict_value_to_formatted_float(job_files) 
    }



    graph_data_manager = graphsdata.GraphDataManager()
    diskdata = graph_data_manager.list_disk_measures()
    
    # TODO: O diskfree deve ser calculado como gráfico de história.

    table3 = {}
    table3['title'] = u"Ocupação do disco"
    table3['width'] = ""
    table3['type'] = "area"
    table3['cid'] = "chart3"
    table3['height'] = "130"
    # table3['header'] = ["Gigabytes"]
    table3['header'] = [ i[0] for i in diskdata ]
    table3['lines'] = {"Disponível": [ i[1] for i in diskdata ]}



    memory = systeminfo.get_memory_usage()
    memory_free = 100 - memory
    
    table4 = {}
    table4['title'] = u"Uso da memória"
    table4['width'] = "48%"
    table4['type'] = "pie"
    table4['cid'] = "chart4"
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
    table5['cid'] = "chart5"
    table5['header'] = ["Clocks"]
    table5['lines'] = {
        "Disponível": [cpu_free],
        "Ocupado": [cpu]}

    offsite_usage = 55 #TODO
    # offsite_free = 45
    

    offsite_data = graph_data_manager.list_offsite_measures()

    table6 = {}
    table6['title'] = u"Uso do Offsite"
    table6['width'] = ""
    table6['type'] = "area"
    table6['height'] = "130"
    table6['cid'] = "chart6"
    # table6['header'] = ["GB"]
    table6['header'] = [ i[0] for i in offsite_data]
    table6['lines'] = {"Disponível": [ i[1] for i in offsite_data] }


   
    
    # Dados de content:
    # - type
    # - label
    # - date
    # - message
    


    last_jobs = Job.objects.all()\
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


    errors_jobs = Job.objects.filter(jobstatus__in=('e','E','f'))\
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


   
    backups_com_falhas = [{
        'title': u'Últimos backups executados',
        'content': last_procedures_content  }, {
        'title': u'Backups com falha',
        'content': errors_procedures_content   
    }]
    
      
    # extra_content = {'table1': table1, 'table2': table2}


    return render_to_response(request, "home.html", locals())




@login_required
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
