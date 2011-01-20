# -*- coding: UTF-8 -*-
# Create your views here.



from time import strftime, strptime
import simplejson
import xmlrpclib

from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

from nimbus.computers.models import Computer
from nimbus.procedures.models import Profile, Procedure
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from nimbus.schedules.shared import trigger_class, trigger_map
from nimbus.filesets.models import FileSet, FilePath
from nimbus.shared.forms import form_from_model
from nimbus.backup.forms import StorageForm

from nimbus.shared import utils
from nimbus.shared.msgerrors import default_errors
from nimbus.libs.db import Session
from nimbus.shared.enums import days, weekdays, levels, operating_systems
from nimbus.shared.views import render_to_response
from nimbus.pools.models import Pool


@login_required
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
                offsite_on = request.POST.get('offsite_on')
                procedure = Procedure(name=procedure_name, 
                                      offsite_on=offsite_on)
        else:
            errors["procedure_name"] = "Você deve inserir o nome do procedimento"


        try:
            retention_time = int(request.POST.get('retention_time'))
        except ValueError, error:
            errors["retention_time"] = "Informe o tempo de retenção dos arquivos em dias"

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


                                        hour = request.POST.get(trigger + '.hour')
                                        if not hour:
                                            errors['schedule_hour'] = "Você deve informar a hora de execução do agendamento %s" % trigger_map[trigger_name]
                                        else:
                                            if Trigger is Hourly:
                                                hour = strftime("%H:%M", strptime(hour, "%M"))

                                            level = request.POST.get(trigger + '.level')

                                            if not trigger_name in ["dayly", "hourly"]:
                                                post_days = set(request.POST.getlist(trigger + '.day'))

                                                if not post_days:
                                                    errors['schedule_day'] = "Você deve selecionar um dia para a execução do agendamento %s"  % trigger_map[trigger_name]
                                                else:
                                                    for d  in post_days:
                                                        trigger = Trigger(day=d, hour=hour,
                                                                          level=level)
                                                        modeltriggers.append(trigger)
                                            else:
                                                trigger = Trigger(hour=hour,level=level)
                                                modeltriggers.append(trigger)



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
            with Session() as session:
                if not profile.id:
                    if not fileset.id:
                        form = form_from_model(fileset)
                        if form.is_valid():
                            fileset.save()
                            session.add(fileset)
                            for filepath in paths:
                                path,created = FilePath.objects.get_or_create(path=filepath)
                                session.add(path)
                                path.filesets.add( fileset )
                                form = form_from_model(path)
                                if form.is_valid():
                                    path.save()

                    if not schedule.id:
                        form = form_from_model(schedule)
                        if form.is_valid():
                            schedule.save()
                            session.add(schedule)
                            for trigger in modeltriggers:
                                trigger.schedule = schedule
                                form = form_from_model(trigger)
                                if form.is_valid():
                                    trigger.save()
                                    session.add(trigger)


                    profile.storage = storage
                    profile.schedule = schedule
                    profile.fileset = fileset
                    form = form_from_model(profile)
                    if form.is_valid():
                        profile.save()
                        session.add(profile)


                procedure.computer = computer
                procedure.profile = profile
                form = form_from_model(procedure)
                if form.is_valid():
                    procedure.pool = Pool.objects.create(name=procedure.name,
                                                         retention_time=retention_time)
                    procedure.save()
                    session.add(procedure)


                messages.success(request, u"Backup adicionado com sucesso.")
                return redirect('nimbus.procedures.views.list')



    else:
        # NOT GET OR POST
        pass





@login_required
def get_tree(request):

    if request.method == "POST":
        path = request.POST['path']
        computer_id = request.POST['computer_id']

        computer = Computer.objects.get(id=computer_id)

        url = "http://%s:%d" % (computer.address, settings.NIMBUS_CLIENT_PORT)
        proxy = xmlrpclib.ServerProxy(url)

        if computer.operation_system == "windows" and path == "/":
            files = proxy.get_available_drives()
            files = [ fname[:-1] + '/' for fname in files ]
        else:
            files = proxy.list_dir(path)
        files.sort()
        
        response = simplejson.dumps(files)
        return HttpResponse(response, mimetype="text/plain")
    
