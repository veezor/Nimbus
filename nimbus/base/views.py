# -*- coding: utf-8 -*-
# Create your views here.

import simplejson
import systeminfo


from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from nimbus.shared import utils
from nimbus.shared.views import render_to_response
from nimbus.bacula.models import Job
from nimbus.libs import graphsdata
from nimbus.base.models import Notification
from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer

@login_required
def notifications(request):
    notifications = Notification.objects.filter(ack=False)
    notes = []
    for note in notifications:
        notes.append({"id": note.id, "message": note.message, "link": note.link})
    response = simplejson.dumps(notes)
    return HttpResponse(response)

@login_required
def ack_notification(request):
    note_id = request.GET['id']
    note = Notification.objects.get(id=note_id)
    note.ack = True
    note.save()
    return HttpResponse("")


@login_required
def home(request):
    job_bytes = Job.get_bytes_from_last_jobs()
    table1 = {
        'title': u"Quantidade de dados realizados backup", 'width': "100%",
        'type': "bar",
        'cid': "chart1",
        'header': [d.strftime("%d/%m/%y") for d in sorted(job_bytes)],
        'labels': [utils.filesizeformat(v) for k, v in sorted(job_bytes.items())],
        'lines': {
            "Dados": utils.ordered_dict_value_to_formatted_float(job_bytes)
        }
    }

    job_files = Job.get_files_from_last_jobs()
    table2 = {
        'title': u"Quantidade de arquivos realizados backup", 'width': "100%",
        'type': "bar",
        'cid': "chart2",
        'header': [d.strftime("%d/%m/%y") for d in sorted(job_files)],
        'labels': [int(v) for k, v in sorted(job_files.items())],
        'lines': {
            "Arquivos": [int(v) for k, v in sorted(job_files.items())]
        }
    }

    graphsdata.update_disk_graph()
    graph_data_manager = graphsdata.GraphDataManager()
    diskdata = graph_data_manager.list_disk_measures()
    

    table3 = {'title': u"Ocupação do disco (GB)", 'width': "", 'type': "area", 'cid': "chart3", 'height': "200",
              'header': [i[0] for i in diskdata], 'labels': [utils.filesizeformat(i[1], "GB") for i in diskdata]}
    #table3['header'] = ["Gigabytes"]
    #setando valor padrao
    t3data = [utils.filesizeformat(i[1], "GB") for i in diskdata] if len(diskdata) else [0.0]
    table3['lines'] = {"Disponível": t3data}


    memory = systeminfo.get_memory_usage()
    memory_free = 100 - memory

    table4 = {'title': u"Uso da memória", 'width': "90%", 'type': "pie", 'cid': "chart4", 'header': ["Gigabytes"],
              'lines': {
                  "Disponível": [memory_free],
                  "Ocupado": [memory]}}

    cpu = systeminfo.get_cpu_usage()
    cpu_free = 100 - memory


    table5 = {'title': u"Uso da CPU", 'width': "", "type": "pie", 'cid': "chart5", 'header': ["Clocks"], 'lines': {
        "Disponível": [cpu_free],
        "Ocupado": [cpu]}}

    #offsite_usage = 55 #TODO
    #offsite_free = 45


    offsite_data = graph_data_manager.list_offsite_measures()
    table6 = False
    if len(offsite_data) > 0:
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

    last_jobs = Procedure.all_non_self_jobs()[:5]

    return render_to_response(request, "home.html", locals())

def ie_error(request):
    return render_to_response(request, "ie_error.html", locals())
    
def license(request):
    return render_to_response(request, "license_general.html", locals())

def about(request):
    version_file = settings.VERSION_FILE

    with file(version_file) as f:
        version_content = f.read().strip()


    version, githash = version_content.split('-')

    computers = len(Computer.objects.exclude(id=1))
    all_procedures = Procedure.objects.exclude(id=1)
    jobs = 0
    for procedure in all_procedures:
        jobs += len(procedure.all_my_good_jobs)
    procedures = len(all_procedures)

    try:
        last_backup = Procedure.objects.get(id=1).last_success_date().endtime.strftime("%d/%m/%Y - %H:%M:%S")
    except IndexError:
        last_backup = "Não realizado"

    data = {'computers': computers,
            'procedures': procedures,
            'jobs': jobs,
            'last_backup': last_backup,
            'version': version,
            'release': githash
            }
    return render_to_response(request, "about.html", data)


