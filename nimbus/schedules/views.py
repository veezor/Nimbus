# Create your views here.
# -*- coding: UTF-8 -*-

import traceback

import socket
from django.http import HttpResponse
from nimbus.computers.models import Computer
from django.shortcuts import render_to_response
import simplejson
from nimbus.schedules import forms
from nimbus.shared.enums import levels, days_range, weekdays_range, end_days_range
from nimbus.schedules.models import Schedule as Schedule_obj


def add(request):
    lforms = [ forms.ScheduleForm(prefix="schedule") ]
    schedule_forms = forms.make_schedule_form_container()
    schedule_forms.get()
    content = {
        'title':u'Criar Agendamento',
        'levels':levels,
        'forms':lforms,
        'formset':schedule_forms,
        'days':days_range,
        'end_days':end_days_range,
        'weekdays':weekdays_range
    }
    return render_to_response('add_schedules.html', content)

def edit(request, object_id):
    print object_id
    schedule = Schedule_obj.objects.get(id=object_id)
    template = 'base_schedules.html'
    lforms = [ forms.ScheduleForm(prefix="schedule", instance=schedule) ]
    schedule_forms = forms.make_schedule_form_container(schedule)
    schedule_forms.get()
    extra_content = {
        'title':u'Editar Agendamento',
        'levels':levels,
        'forms':lforms,
        'formset':schedule_forms,
        'days':days_range,
        'end_days':end_days_range,
        'weekdays':weekdays_range
    }
    return render_to_response(template, extra_content)

def render(request, object_id=0):

    lforms = [ forms.ScheduleForm(prefix="schedules", initial={'computer':object_id}) ]


    content = {
        'title':u'Criar Backup',
        'forms':lforms,
        'computer_id':object_id
    }
    return render_to_response("backup_add.html", content)

def profile_new(request):
    lforms = [ forms.ProfileForm(prefix="profile") ]
    content = {
        'title':u'Criar Perfil de Backup',
        'forms':lforms
    }
    return render_to_response("profile_new.html", content)

def schedule_new(request):
    if request.method == "POST":
        print request.POST
    lforms = [ forms.ScheduleForm(prefix="schedule") ]
    schedule_forms = forms.make_schedule_form_container()
    schedule_forms.get()
    days_range = range(1, 32)
    weekdays_range = {0:'Domingo', 1:'Segunda', 2:'Terca', 3:'Quarta', 4:'Quinta', 5:'Sexta', 6:'Sabado'}
    end_days_range = [5, 10, 15, 20, 25, 30]
    content = {'title':u'Criar Agendamento', 'forms':lforms, 'formset':schedule_forms, 'days':days_range, 'end_days':end_days_range, 'weekdays':weekdays_range}
    return render_to_response("schedule_new.html", content)

def fileset_new(request, object_id):
    # apenas teste, remover em modo de produção
    if request.method == "POST":
        print request.POST
    lforms = [ forms.FileSetForm(prefix="fileset") ]
    lformsets = [ forms.FilePathForm(prefix="filepath") ]
    formset = forms.FilesFormSet()
    content = {'title':u'Criar Sistema de Arquivos', 'forms':lforms, 'formsets':lformsets, 'computer_id':object_id,
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





# # -*- coding: utf-8 -*-
# 
# from time import strftime, strptime
# 
# 
# from django.shortcuts import redirect
# from django.core.exceptions import ValidationError
# from django.contrib.auth.decorators import login_required
# 
# from nimbus.schedules.models import Schedule, Hourly
# from nimbus.schedules.forms import (ScheduleForm, DailyForm, MonthlyForm,
#                                     HourlyForm, WeeklyForm)
# from nimbus.schedules.shared import trigger_class, trigger_map
# from nimbus.shared.views import render_to_response
# from nimbus.shared import utils
# from nimbus.libs.db import Session
# 
# from django.contrib import messages
# from nimbus.shared.enums import days, weekdays, levels, operating_systems
# 
# 
# @login_required
# def add(request):
#     title = u"Criar agendamento"
# 
#     schedule_form = ScheduleForm()
#     daily_form = DailyForm()
#     monthly_form = MonthlyForm()
#     hourly_form = HourlyForm()
#     weekly_form = WeeklyForm()
# 
#     extra_content = {
#         'days': days,
#         'weekdays': weekdays,
#         'levels': levels,
#         'operating_systems': operating_systems,
#         'schedule_form': schedule_form
#     }
#     extra_content.update(**locals())
# 
#     if request.method == 'POST':
#         # TODO: Save.
#         pass
# 
#     return render_to_response(request, 'add_schedules.html', extra_content)
# 
# 
# @login_required
# def edit(request, object_id):
# 
#     schedule = Schedule.objects.get(id=object_id)
#     title = u"Editar agendamento"
#     template = 'base_schedules.html'
# 
# 
#     extra_content = {
#         'days': days,
#         'weekdays': weekdays,
#         'levels': levels,
#         'operating_systems': operating_systems,
#     }
#     extra_content.update(**locals())
# 
#     if request.method == "GET":
#         return render_to_response(request, template, extra_content)
# 
# 
#     if request.method == "POST":
# 
# 
#         errors = {}
#         extra_content["errors"] =  errors
# 
#         schedule = Schedule.objects.get(id=object_id)
# 
#         template = 'edit_schedules.html'
#         schedule_name = request.POST.get('schedule.name')
# 
#         try:
#             old_schedule = Schedule.objects.get(name=schedule_name)
#         except Schedule.DoesNotExist, notexist:
#             old_schedule = None
# 
#         if (not old_schedule is None) and old_schedule != schedule:
#             errors["schedule_name"] = "Nome não disponível. Já existe um agendamento com este nome"
# 
# 
#         with Session() as session:
# 
#             if schedule_name:
# 
#                 schedule.name = schedule_name
# 
# 
#                 selected_a_trigger = False
#                 triggers = ["schedule.monthly", "schedule.dayly", "schedule.weekly", "schedule.hourly"]
# 
# 
#                 for trigger in triggers:
# 
#                     selected_a_trigger = True
#                     is_trigger_edit = False
# 
#                     trigger_name = trigger[len("schedule."):]
#                     Trigger = trigger_class[trigger_name]
# 
#                     old_triggers = [ t for t in schedule.get_triggers() if isinstance(t, Trigger) ]
# 
#                     if old_triggers:
#                         is_trigger_edit = True
# 
#                     if not request.POST.get(trigger + '.active'):
# 
#                         for t in old_triggers:
#                             t.delete()
#                             session.delete(t)
# 
#                     else: # active
# 
#                         hour = request.POST.get(trigger + '.hour')
#                         if not hour:
#                             errors['schedule_hour'] = "Você deve informar a hora de execução do agendamento %s" % trigger_map[trigger_name]
#                         else:
#                             if Trigger is Hourly:
#                                 hour = strftime("%H:%M", strptime(hour, "%M"))
# 
#                             level = request.POST.get(trigger + '.level')
# 
#                             if not trigger_name in ["dayly", "hourly"]:
#                                 post_days = set(request.POST.getlist(trigger + '.day'))
# 
#                                 if not post_days and not is_trigger_edit:
#                                     errors['schedule_day'] = "Você deve selecionar um dia para a execução do agendamento %s"  % trigger_map[trigger_name]
#                                 else:
#                                     old_days = set([ unicode(t.day) for t in old_triggers ])
# 
#                                     if len(old_days) != len(post_days):
#                                         new_days = post_days - old_days
#                                         remove_days =  old_days - post_days
# 
#                                         for d in remove_days:
#                                             t = Trigger.objects.get(day=d,schedule=schedule)
#                                             t.delete()
#                                             session.delete(t)
# 
#                                         for d  in new_days:
#                                             Trigger.objects.create(day=d,
#                                                                    hour=hour,
#                                                                    level=level,
#                                                                    schedule=schedule)
#                             else:
#                                 try:
#                                     trigger = Trigger.objects.get(schedule=schedule)
#                                 except Trigger.DoesNotExist, error:
#                                     trigger = Trigger()
#                                     trigger.schedule = schedule
# 
#                                 trigger.hour = hour
#                                 trigger.level = level
#                                 session.add(trigger)
#                                 try:
#                                     trigger.save()
#                                 except ValidationError, error:
#                                     errors['schedule_hour'] = 'Horário do agendamento errado'
# 
# 
# 
#                             is_trigger_edit = False
# 
#                 if not selected_a_trigger:
#                     errors['schedule_name'] = "Você deve ativar pelo menos um tipo de agendamento"
# 
#             else:
#                 errors['schedule_name'] = "Você deve inserir um nome na configuração do agendamento"
# 
#             if not errors:
#                 schedule.save()
#                 session.add(schedule)
#                 messages.success(request, u"Agendamento atualizado com sucesso.")
#                 return redirect('nimbus.schedules.views.edit', object_id)
#             else:
#                 session.rollback()
#                 extra_content.update(**locals())
#                 extra_content.update( utils.dict_from_querydict(
#                                             request.POST,
#                                             lists=("schedule_monthly_day",
#                                                    "schedule_dayly_day",
#                                                    "schedule_hourly_day",
#                                                    "schedule_weekly_day")) )
# 
#                 return render_to_response(request, template, extra_content )