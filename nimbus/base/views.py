# -*- coding: utf-8 -*-
# Create your views here.


from django.contrib.auth.decorators import login_required
from nimbus.shared.views import render_to_response

@login_required
def home(request):
    table1 = {}
    table1['title'] = u"Quantidade de backups executados por armazenamento"
    table1['type'] = "bar"
    table1['header'] = ["10/02/2010", "10/03/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010"]
    table1['lines'] = {
        "Principal": ["20", "22", "27", "25", "35", "21", "25", "35", "21"],
        "Secundário": ["17", "20", "28", "31", "26", "20", "31", "26", "20"]}
    
    table2 = {}
    table2['title'] = u"Bytes trafegados no backup Offsite"
    table2['type'] = "area"
    table2['header'] = ["10/02/2010", "10/03/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010"]
    table2['lines'] = {
        "Out": ["145", "197", "244", "37", "397", "233", "791", "981", "112"],
        "In": ["17", "20", "28", "31", "26", "20", "31", "26", "20"]}
    
    extra_content = {'table1': table1, 'table2': table2}
    return render_to_response(request, "home.html", extra_content)

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
