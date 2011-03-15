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
    table1['title'] = u"Quantidade de dados realizados backup"
    table1['width'] = "100%"
    table1['type'] = "bar"
    table1['cid'] = "chart1"
    table1['header'] = [ d.strftime("%d/%m/%y") for d in sorted(job_bytes)  ]
    table1['labels'] = [ utils.filesizeformat(v) for k,v in sorted(job_bytes.items()) ]

    table1['lines'] = {
        "Dados": utils.ordered_dict_value_to_formatted_float(job_bytes)
    }

    job_files = Job.get_files_from_last_jobs()
    table2 = {}
    table2['title'] = u"Quantidade de arquivos realizados backup"
    table2['width'] = "100%"
    table2['type'] = "bar"
    table2['cid'] = "chart2"
    table2['header'] = [ d.strftime("%d/%m/%y") for d in sorted(job_files) ]
    table2['labels'] = [ v for k,v in sorted(job_files.items()) ]
    table2['lines'] = {
        "Arquivos": [ v for k,v in sorted(job_files.items()) ]
    }



    graph_data_manager = graphsdata.GraphDataManager()
    diskdata = graph_data_manager.list_disk_measures()
    diskdata = [("13/11", 2), ("13/01", 25), ("13/01", 27), ("13/01", 10), ("16/01", 15), ("16/01", 15),
                ("16/01", 12), ("16/01", 28)]
    if len(diskdata) == 1: # duplicates first item for area graph
        diskdata *= 2



    # TODO: O diskfree deve ser calculado como gráfico de história.

    table3 = {}
    table3['title'] = u"Ocupação do disco"
    table3['width'] = ""
    table3['type'] = "area"
    table3['cid'] = "chart3"
    table3['height'] = "130"
    # table3['header'] = ["Gigabytes"]
    table3['header'] = [ i[0] for i in diskdata ]
    table3['labels'] = [ utils.filesizeformat(i[1]) for i in diskdata ]
    #setando valor padrao
    t3data = [i[1] for i in diskdata] if len(diskdata) else [0.0]
    table3['lines'] = {"Disponível": t3data}


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

    if len(offsite_data) == 1: # duplicates first item for area graph
        offsite_data *= 2

    table6 = {}
    table6['title'] = u"Uso do Offsite"
    table6['width'] = ""
    table6['type'] = "area"
    table6['height'] = "130"
    table6['cid'] = "chart6"
    # table6['header'] = ["GB"]
    table6['header'] = [ i[0] for i in offsite_data]
    table6['labels'] = [ utils.filesizeformat(i[1]) for i in offsite_data ]
    t6data = [i[1] for i in offsite_data] if len(offsite_data) else [0.0]
    table6['lines'] = {"Disponível": t6data }

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
                'tooltip' : job.status_message,
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
                'tooltip' : job.status_message,
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




