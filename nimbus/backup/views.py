# -*- coding: UTF-8 -*-
# Create your views here.


import os
from glob import glob
import simplejson

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from nimbus.computers.models import Computer
from nimbus.procedures.models import Profile, Procedure
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.backup.forms import StorageForm

from nimbus.shared.enums import days, weekdays, levels, operating_systems
from nimbus.shared.views import render_to_response

def backup_form(request, object_id=None):

    if request.method == "GET":

        if object_id:
            computer = Computer.objects.get(id=object_id)
        else:
            computer = None
        
        computers = Computer.objects.all()
        profiles = Profile.objects.all()
        storages = Storage.objects.all()
        schedules = Schedule.objects.all()
        filesets = FileSet.objects.all()
        
        extra_context = {
            'title': u"Criar Backup",
            'computer': computer,
            'computers': computers,
            'profiles': profiles,
            'storages': storages,
            'days': days,
            'weekdays': weekdays,
            'levels': levels,
            'operating_systems': operating_systems,
            'schedules': schedules,
            'filesets': filesets,
        }

        return render_to_response(request, "backup_create.html", extra_context )

    elif request.method == "POST":

        print request.POST

        try:
            computer = Computer.objects.get(id=request.POST['computer_id'])
        except Computer.DoesNotExist, error:
            print "computador nao existe",object_id


        try:
            profile = Profile.objects.get(id=request.POST['profile_id'])
        except (Profile.DoesNotExist, ValueError), error:
            profile = Profile()
            profile.name = request.POST['profile.name']
            profile.storage = Storage.objects.get(id=request.POST['profile.storage_id'])

        try: 
            schedule = Schedule.objects.get(id=request.POST['profile.schedule_id'])
        except (Schedule.DoesNotExist, ValueError), error:
            schedule = Schedule()
            schedule.name = request.POST['schedule.name']
    else:
        pass




erros = {
        "procedure_name" : "Nome não disponível. Já existe um procedimento com esse nome.",
        "computer_id" : "Computador inválido. Computador não existe.",
        "profile_id" : "Perfil de configuração inválido, não existe.",
        "profile.storage_id" : "Dispositivo de armazenamento inválido, não existe",
        "profile.schedule_id" : "Agendamento inválido, não existe",
        "profile.fileset_id" : "Conjunto de arquivos inválido, não existe",
        "schedule_name" : "Nome de agendamento inválido, já existente"
}


def add(request):
    if request.method == "POST":
        print request.POST
        # import pdb; pdb.set_trace()
        
        ### Campos que serão recebidos nesta função:
        
        # procedure_name - str
        # computer_id - int
        # profile_id - int
        # 
        # profile.storage_id - int
        # profile.schedule_id - int
        # profile.fileset_id - int
        # 
        # schedule.name - str
        # 
        # schedule.monthly.active - bool
        # schedule.monthly.day - list
        # schedule.monthly.hour - str
        # schedule.monthly.level - int
        # 
        # schedule.weekly.active - bool
        # schedule.weekly.day - list
        # schedule.weekly.hour - str
        # schedule.weekly.level - int
        # 
        # schedule.dayly.active - bool
        # schedule.dayly.day - list
        # schedule.dayly.hour - str
        # schedule.dayly.level - int
        # 
        # schedule.hourly.active - bool
        # schedule.hourly.day - list
        # schedule.hourly.hour - str
        # schedule.hourly.level - int
        
        ## Exemplo do objeto.
        # {
        # u'schedule.monthly.level': [u'Full'],
        # u'procedure_name': [u'asdasdas'],
        # u'schedule.dayly.level': [u'Full'],
        # u'profile.schedule_id': [u'Criar novo agendamento'],
        # u'schedule.weekly.active': [u'1'],
        # u'schedule.dayly.hour': [u''],
        # u'computer_id': [u'1'],
        # u'schedule.weekly.level': [u'Full'],
        # u'profile_id': [u''],
        # u'profile.fileset_id': [u'2'],
        # u'schedule.hourly.minute': [u''],
        # u'fileset_name': [u'', u'', u''],
        # u'schedule.monthly.hour': [u'13:00'],
        # u'profile.storage_id': [u'1'],
        # u'schedule.weekly.day[]': [u'mon', u'wed'],
        # u'schedule.hourly.level': [u'Full'],
        # u'schedule.weekly.hour': [u'21:00'],
        # u'schedule.monthly.day[]': [u'1', u'17', u'29'],
        # u'schedule.monthly.active': [u'1']
        # }


def is_dir(name):
    if os.path.isdir(name):
        return name + "/" 
    return name


def get_tree(request):

    if request.method == "POST":
        path = request.POST['path']
        computer_id = request.POST['computer_id']
        files = glob(path + "*")
        files.sort()
        files = map(is_dir, files)
        response = simplejson.dumps(files)
        return HttpResponse(response, mimetype="text/plain")
    
