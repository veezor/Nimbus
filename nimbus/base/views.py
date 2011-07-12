# -*- coding: utf-8 -*-
# Create your views here.

import operator

import systeminfo

import re

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from nimbus.shared import utils, middlewares
from nimbus.shared.views import render_to_response
from nimbus.bacula.models import Job
from nimbus.libs import graphsdata

from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer


@login_required
def home(request):
    job_bytes = Job.get_bytes_from_last_jobs()
    table1 = {
        'title': u"Quantidade de dados realizados backup", 'width': "100%", 'type': "bar", 'cid': "chart1",
        'header': [d.strftime("%d/%m/%y") for d in sorted(job_bytes)],
        'labels': [utils.filesizeformat(v) for k, v in sorted(job_bytes.items())],
        'lines': {
            "Dados": utils.ordered_dict_value_to_formatted_float(job_bytes)
        }
    }

    job_files = Job.get_files_from_last_jobs()
    table2 = {
        'title': u"Quantidade de arquivos realizados backup", 'width': "100%",
        'type': "bar", 'cid': "chart2",
        'header': [d.strftime("%d/%m/%y") for d in sorted(job_files)],
        'labels': [int(v) for k, v in sorted(job_files.items())],
        'lines': {
            "Arquivos": [int(v) for k, v in sorted(job_files.items())]
        }
    }

    graph_data_manager = graphsdata.GraphDataManager()
    diskdata = graph_data_manager.list_disk_measures()
    diskdata = [("13/11", 2), ("13/01", 25), ("13/01", 27), ("13/01", 10), ("16/01", 15), ("16/01", 15),
                ("16/01", 12), ("16/01", 28)]
    if len(diskdata) == 1: # duplicates first item for area graph
        diskdata *= 2

    # TODO: O diskfree deve ser calculado como gráfico de história.

    table3 = {'title': u"Ocupação do disco", 'width': "", 'type': "area", 'cid': "chart3", 'height': "130",
              'header': [i[0] for i in diskdata], 'labels': [utils.filesizeformat(i[1]) for i in diskdata]}
    # table3['header'] = ["Gigabytes"]
    #setando valor padrao
    t3data = [i[1] for i in diskdata] if len(diskdata) else [0.0]
    table3['lines'] = {"Disponível": t3data}


    memory = systeminfo.get_memory_usage()
    memory_free = 100 - memory

    table4 = {'title': u"Uso da memória", 'width': "48%", 'type': "pie", 'cid': "chart4", 'header': ["Gigabytes"],
              'lines': {
                  "Disponível": [memory_free],
                  "Ocupado": [memory]}}

    cpu = systeminfo.get_cpu_usage()
    cpu_free = 100 - memory


    table5 = {'title': u"Uso da CPU", 'width': "48%", "type": "pie", 'cid': "chart5", 'header': ["Clocks"], 'lines': {
        "Disponível": [cpu_free],
        "Ocupado": [cpu]}}

    #offsite_usage = 55 #TODO
    #offsite_free = 45


    offsite_data = graph_data_manager.list_offsite_measures()
    print "a" * 200
    print len(offsite_data)
    table6 = False
    if len(offsite_data) > 0:
        if len(offsite_data) == 1: # duplicates first item for area graph
            offsite_data *= 2
        table6 = {'title': u"Uso do Offsite", 'width': "", 'type': "area", 'height': "130", 'cid': "chart6",
                  'header': [i[0] for i in offsite_data], 'labels': [utils.filesizeformat(i[1]) for i in offsite_data]}
        # table6['header'] = ["GB"]
        t6data = [i[1] for i in offsite_data] if len(offsite_data) else [0.0]
        table6['lines'] = {"Disponível": t6data }

    # Dados de content:
    # - type
    # - label
    # - date
    # - message

    last_jobs = Job.objects.all().order_by('-starttime').distinct()[:5]
    
    # detects browser
    
    browser = request.META['HTTP_USER_AGENT']
    init_message = ""
    if re.search("MSIE", browser):
        annoying_message = ".annoying{display: block;}"
        init_message = "$(document).ready(function(){$.facebox.settings.opacity = 0.5;jQuery.facebox({ ajax : ie_error});});"

    return render_to_response(request, "home.html", locals())

def ie_error(request):
    return render_to_response(request, "ie_error.html", locals())



