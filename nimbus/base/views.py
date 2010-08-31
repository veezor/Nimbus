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
    table2['type'] = "line"
    table2['header'] = ["10/02/2010", "10/03/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010", "10/02/2010"]
    table2['lines'] = {
        "Out": ["145", "197", "244", "37", "397", "233", "791", "981", "112"],
        "In": ["17", "20", "28", "31", "26", "20", "31", "26", "20"]}
    
    extra_content = {'table1': table1, 'table2': table2}
    return render_to_response(request, "home.html", extra_content)
