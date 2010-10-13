# -*- coding: UTF-8 -*-
# Create your views here.


import os
from glob import glob
import simplejson


from django.db import transaction
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from nimbus.computers.models import Computer
from nimbus.procedures.models import Profile, Procedure
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from nimbus.filesets.models import FileSet, FilePath
from nimbus.backup.forms import StorageForm

from nimbus.shared import utils
from nimbus.shared.enums import days, weekdays, levels, operating_systems
from nimbus.shared.views import render_to_response


default_errors = {
        "procedure_name" : "Nome não disponível. Já existe um procedimento com esse nome.",
        "computer_name" : "Computador inválido. Computador não existe.",
        "computer_id" : "Você deve selecionar um computador.",
        "profile_id" : "Perfil de configuração inválido, não existe.",
        "profile_storage_id" : "Você deve selecionar um dispositivo de armazenamento.",
        "profile_schedule_id" : "Agendamento inválido, não existe.",
        "profile_fileset_id" : "Conjunto de arquivos inválido, não existe.",
        "schedule_name" : "Nome de agendamento inválido, já existente."
}


trigger_map = {
        "monthly" : "mensal",
        "dayly" : "diário",
        "hourly" : "minuto",
        "weekly" : "semanal",
}

trigger_class = {
        "monthly" : Monthly,
        "dayly" : Daily,
        "hourly" : Hourly,
        "weekly" : Weekly,
}



@transaction.commit_manually
def backup_form(request, object_id=None):

    errors = {}

    computers = Computer.objects.all()
    profiles = Profile.objects.all()
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
   
    extra_context = {
        'title': u"Criar Backup",
        'computers': computers,
        'profiles': profiles,
        'storages': storages,
        'days': days,
        'weekdays': weekdays,
        'levels': levels,
        'operating_systems': operating_systems,
        'schedules': schedules,
        'filesets': filesets,
        'errors' : errors,
    }

    if request.method == "GET":

        try:
            computer = Computer.objects.get(id=object_id)
        except (Computer.DoesNotExist, ValueError), error:
            computer = None

        extra_context["computer"] = computer

        return render_to_response(request, "backup_create.html", extra_context )

    elif request.method == "POST":

        
        modeltriggers = []
        modelpaths = []


        procedure_name = request.POST.get('procedure_name')
        if procedure_name:
            try: 
                procedure = Procedure.objects.get(name=procedure_name)
                key = "procedure_name"
                errors[key] = default_errors[key]
            except (Procedure.DoesNotExist), error:
                procedure = Procedure(name=procedure_name)
        else:
            errors["procedure_name"] = "Você deve inserir o nome do procedimento"



        try:
            computer = Computer.objects.get(id=request.POST['computer_id'])
        except Computer.DoesNotExist, error:
            key = "computer_id"
            errors[key] = default_errors[key]
        except ValueError, error:
            key = "computer_id"
            errors[key] = default_errors[key]


        profile_id = request.POST.get('profile_id')

        if profile_id:

            try:
                profile = Profile.objects.get(id=request.POST['profile_id'])
            except ValueError, error:

                profile_name = request.POST.get('profile.name')

                try:
                    has_profile = Profile.objects.get(name=profile_name)
                    errors["profile_name"] = "Nome inválido. Já existe um perfil de configuração com esse nome"
                except Profile.DoesNotExist, notexist:
                    if profile_name:
                        profile = Profile(name=profile_name)
                    else:
                        errors['profile_name'] = "Você deve inserir um nome no perfil de configuração"
                
                
                storage_id = request.POST.get('profile.storage_id')

                if storage_id:
                    try:
                        storage = Storage.objects.get(id=storage_id)
                    except (Storage.DoesNotExist, ValueError), error:
                        key = "profile_storage_id"
                        errors[key] = default_errors[key]
                else:
                    key = "profile_storage_id"
                    errors[key] = default_errors[key]

                try:
                    schedule_id = request.POST['profile.schedule_id']
                    schedule = Schedule.objects.get(id=schedule_id)
                except ValueError, error:

                    if schedule_id == "new_schedule":
                        schedule_name = request.POST.get('schedule.name')

                        try:
                            has_schedule = Schedule.objects.get(name=schedule_name)
                            key = "schedule_name"
                            errors[key] = default_errors[key]
                        except Schedule.DoesNotExist, notexist:

                            if schedule_name:
                                schedule = Schedule(name = schedule_name)

                                selected_a_trigger = False

                                triggers = ["schedule.monthly", "schedule.dayly", "schedule.weekly", "schedule.hourly"]


                                for trigger in triggers:

                                    if request.POST.get(trigger + '.active'):


                                        selected_a_trigger = True
                                        trigger_name = trigger[len("schedule."):]
                                        Trigger = trigger_class[trigger_name]

                                        modeltrigger = Trigger()



                                        if not trigger_name in ["dayly", "hourly"]:
                                            day = request.POST.getlist(trigger + '.day')

                                            if not day:
                                                errors['schedule_day'] = "Você deve selecionar um dia para a execução do agendamento %s"  % trigger_map[trigger_name]
                                            else:
                                                modeltrigger.day = day

                                        hour = request.POST.get(trigger + '.hour')

                                        if not hour:
                                            errors['schedule_hour'] = "Você deve informar a hora de execução do agendamento %s" % trigger_map[trigger_name]
                                        else:
                                            if isinstance(modeltrigger, Hourly):
                                                hour = strftime("%H:%M", strptime(hour, "%M"))

                                            modeltrigger.hour = hour

                                        level = request.POST.get(trigger + '.level')

                                        modeltrigger.level = level

                                        modeltriggers.append(modeltrigger)

                                if not selected_a_trigger:
                                    errors['schedule_name'] = "Você deve ativar pelo menos um tipo de agendamento"

                            else:
                                errors['schedule_name'] = "Você deve inserir um nome na configuração do agendamento"
                    else:
                        errors['profile_schedule_id'] = "Você deve selecionar um agendamente ou criar um novo"



                try: 
                    fileset_id = request.POST['profile.fileset_id']
                    fileset = FileSet.objects.get(id=fileset_id)
                except ValueError, error:

                    if fileset_id == "new_fileset":


                        fileset_name = request.POST.get('fileset_name')


                        try:
                            has_fileset = FileSet.objects.get(name=fileset_name)
                            errors["fileset_name"] = "Nome inválido. Já existe um conjunto de arquivos com esse nome"
                        except FileSet.DoesNotExist, notexist:
                            if fileset_name:
                                fileset = FileSet(name=fileset_name)
                            else:
                                errors['fileset_name'] = "Você deve inserir um nome para o conjunto de arquivos"

                            paths = request.POST.getlist('path')
                            if not paths:
                                errors['path'] = "Você deve selecionar pelo menos um arquivo para backup"

                    else:
                        errors['profile_fileset_id'] = "Você deve selecionar um conjunto de arquivos ou criar um novo"




        else:
            errors["profile_id"] = "Você deve selecionar um perfil de configuração"

        if errors:
            extra_context.update( utils.dict_from_querydict(
                                        request.POST,
                                        lists=("path", 
                                               "schedule_monthly_day",
                                               "schedule_dayly_day",
                                               "schedule_hourly_day",
                                               "schedule_weekly_day")) )

            return render_to_response(request, "backup_create.html", extra_context )
        else:
            try:
                if not profile.id:
                    if not fileset.id:
                        fileset.full_clean()
                        fileset.save()
                        for filepath in paths:
                            path,created = FilePath.objects.get_or_create(path=filepath)
                            path.fileset = fileset
                            path.full_clean()
                            path.save()

                    if not schedule.id:
                        schedule.full_clean()
                        schedule.save()
                        for trigger in modeltriggers:
                            trigger.schedule = schedule
                            trigger.full_clean()
                            trigger.save()


                    profile.storage = storage
                    profile.schedule = schedule
                    profile.fileset = fileset
                    profile.full_clean()
                    profile.save()


                procedure.computer = computer
                procedure.profile = profile
                procedure.full_clean()
                procedure.save()


            except ValidationError, error:
                transaction.rollback()
            else:
                transaction.commit()
                messages.success(request, u"Backup adicionado com sucesso.")
                return redirect('nimbus.procedures.views.list')



    else:
        # NOT GET OR POST
        pass


def add(request):
    if request.method == "POST":
        pass
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
    
