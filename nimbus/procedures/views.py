# -*- coding: utf-8 -*-
# Create your views here.



from time import strftime, strptime

from django.contrib.auth.decorators import login_required
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages


from nimbus.bacula.models import Job
from nimbus.procedures.models import Procedure, Profile
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from nimbus.filesets.models import FileSet, FilePath
from nimbus.schedules.shared import trigger_class, trigger_map
from nimbus.shared.msgerrors import default_errors
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form, form_mapping, form_from_model
from nimbus.shared.enums import days as days_enum, weekdays as weekdays_enum, levels as levels_enum
from nimbus.procedures.forms import ProfileForm

from nimbus.shared import utils
from nimbus.libs.db import Session



@login_required
def add(request):
    extra_context = {'title': u"Adicionar procedimento"}
    return create_update.create_object( request, 
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



@login_required
def edit(request, object_id):
    extra_context = {'title': u"Editar procedimento"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



@login_required
def delete(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.delete()
        messages.success(request, u"Procedimento removido com sucesso.")
        return redirect('nimbus.procedures.views.list')
    else:
        procedure = Procedure.objects.get(id=object_id)
        remove_name = procedure.name
        return render_to_response(request, 'remove.html', locals())


@login_required
def execute(request, object_id):
    
    procedure = Procedure.objects.get(id=object_id)
    procedure.run()
    messages.success(request, u"Procedimento em execução.")
    return redirect('nimbus.procedures.views.list')




@login_required
def list(request):
    procedures = Procedure.objects.all()
    title = u"Procedimentos"
    running_status = ('R','p','j','c','d','s','M','m','s','F','B')
    running_jobs = Job.objects.filter( jobstatus__in=running_status)\
                                            .order_by('-starttime').distinct()[:5]


    last_jobs = Job.objects.all()\
                    .order_by('-endtime').distinct()[:5]

    running_procedures_content = []
    try:
        for job in running_jobs:
            running_procedures_content.append({
                'type' : 'ok',
                'label' : job.procedure.name,
                'date' : job.starttime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


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


    
    procedimentos_em_execucao_executados = [{
        'title': u'Procedimentos em execução',
        'content': running_procedures_content
        }, {
        'title': u'Últimos procedimentos executados',
        'content': last_procedures_content   
        }]
    
    return render_to_response(request, "procedures_list.html", locals())



@login_required
def list_offsite(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos com offsite ativo"
    }
    return render_to_response(request, "procedures_list.html", extra_content)


@login_required
def activate_offsite(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    procedure.offsite_on = True
    procedure.save()
    return redirect('/procedures/list')


@login_required
def deactivate_offsite(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    procedure.offsite_on = False
    procedure.save()
    return redirect('/procedures/list')



@login_required
def activate(request, object_id):

    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.active = True
        procedure.save()
        messages.success(request, "Procedimento ativado com sucesso")

    return redirect('/procedures/list')


@login_required
def deactivate(request, object_id):

    if request.method == "POST":

        procedure = Procedure.objects.get(id=object_id)
        procedure.active = False
        procedure.save()
        messages.success(request, "Procedimento desativado com sucesso")

    return redirect('/procedures/list')



@login_required
def profile_list(request):
    title = u"Perfis de configuração"
    profiles = Profile.objects.all()
    return render_to_response(request, "profile_list.html", locals())


@login_required
def profile_add(request):
    title = u"Adicionar perfil de configuração"
    
    # storages = Storage.objects.all()
    # schedules = Schedule.objects.all()
    # filesets = FileSet.objects.all()
    # computers = Computer.objects.all()
    
    profile_form = ProfileForm()
    
    days = days_enum
    weekdays = weekdays_enum
    levels = levels_enum
    errors = {}
    extra_context = locals()

    if request.method == "GET":
        return render_to_response(request, "profile_add.html", extra_context)
    elif request.method == "POST":
        # TODO: Validate profile_form.
        
        modeltriggers = []
        modelpaths = []


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
            schedule_id = request.POST['profile_schedule_id']
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
            fileset_id = request.POST['profile_fileset_id']
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


        if errors:
            extra_context.update( utils.dict_from_querydict(
                                        request.POST,
                                        lists=("path", 
                                               "schedule_monthly_day",
                                               "schedule_dayly_day",
                                               "schedule_hourly_day",
                                               "schedule_weekly_day")) )

            return render_to_response(request, "profile_add.html", extra_context )
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


                messages.success(request, u"Perfil de configuração adicionado com sucesso.")
                return redirect('nimbus.procedures.views.list')
        


@login_required
def profile_edit(request, object_id):
    title = u"Editar perfil de configuração"
    profile = Profile.objects.get(id=object_id)
    
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    
    if request.method == "POST":
        
        if request.POST.get('save_as_new'):
            object_id = None

        form = form_mapping(Profile, request.POST, object_id=object_id)

        if form.is_valid():
            profile = form.save()
            messages.success(request,
                u"Perfil de configuração atualizado com sucesso.")
            return redirect('nimbus.procedures.views.profile_list')
    
    return render_to_response(request, "profile_edit.html", locals())


@login_required
def profile_delete(request, object_id):
    if request.method == "POST":
        profile = Profile.objects.get(id=object_id)
        profile.delete()
        messages.success(request, u"Procedimento removido com sucesso.")
        return redirect('nimbus.procedures.profile_list')
    else:
        profile = Profile.objects.get(id=object_id)
        remove_name = profile.name
        return render_to_response(request, 'remove.html', locals())
