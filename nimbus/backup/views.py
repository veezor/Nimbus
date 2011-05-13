# Create your views here.
# -*- coding: UTF-8 -*-

import traceback
import socket
from django.http import HttpResponse
from nimbus.computers.models import Computer
from django.shortcuts import render_to_response
import simplejson
from nimbus.backup import forms
from nimbus.schedules.views import schedule_new


def render(request, object_id=0):

    lforms = [forms.ProcedureForm(prefix="procedure", initial={'computer':object_id})]
    content = {'title':u'Criar Backup',
               'forms':lforms,
               'computer_id':object_id}
    return render_to_response("backup_add.html", content)

def profile_new(request):
    lforms = [forms.ProfileForm(prefix="profile")]
    content = {'title':u'Criar Perfil de Backup',
               'forms':lforms}
    return render_to_response("profile_new.html", content)

# def schedule_new(request):
#     if request.method == "POST":
#         print request.POST
#     lforms = [forms.ScheduleForm(prefix="schedule")]
#     schedule_forms = forms.make_schedule_form_container()
#     schedule_forms.get()
#     days_range = range(1, 32)
#     weekdays_range = {0:'Domingo',
#                       1:'Segunda',
#                       2:'Terca',
#                       3:'Quarta',
#                       4:'Quinta',
#                       5:'Sexta',
#                       6:'Sabado'}
#     end_days_range = [5, 10, 15, 20, 25, 30]
#     content = {'title':u'Criar Agendamento',
#                'forms':lforms,
#                'formset':schedule_forms,
#                'days':days_range,
#                'end_days':end_days_range,
#                'weekdays':weekdays_range}
#     return render_to_response("schedule_new.html", content)

def fileset_new(request, object_id):
    # just for test, must be removed in production mode
    if request.method == "POST":
        print request.POST
    lforms = [ forms.FileSetForm(prefix="fileset") ]
    lformsets = [ forms.FilePathForm(prefix="filepath") ]
    formset = forms.FilesFormSet()
    content = {'title':u'Criar Sistema de Arquivos',
               'forms':lforms,
               'formsets':lformsets,
               'computer_id':object_id,
               'formset' : formset}
    return render_to_response("fileset_new.html", content)

def get_tree(request):
    if request.method == "POST":
        try:
            path = request.POST['path']
            computer_id = request.POST['computer_id']
            try:
                computer = Computer.objects.get(id=computer_id)
                files = computer.get_file_tree(path)
                response = simplejson.dumps(files)
            except socket.error, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" : "Impossível conectar ao cliente"})
            except Computer.DoesNotExist, error:
                response = simplejson.dumps({"type" : "error",
                                             "message" : "Computador não existe"})
            return HttpResponse(response, mimetype="text/plain")
        except Exception:
            traceback.print_exc()
