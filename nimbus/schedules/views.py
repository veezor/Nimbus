# Create your views here.
# -*- coding: UTF-8 -*-

import traceback
import simplejson
import socket
from copy import copy

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib import messages
from nimbus.computers.models import Computer
from nimbus.schedules import forms
from nimbus.shared.enums import levels, days_range, weekdays_range, end_days_range
from nimbus.shared.views import render_to_response
from nimbus.schedules.models import Schedule

# def edit_do_(request, procedure_id):
#     p = get_object_or_404(Procedure, pk=procedure_id)
#     title = u"Editando '%s'" % p.name
#     partial_form = ProcedureEditForm(prefix="procedure", instance=p)
#     lforms = [partial_form]
#     content = {'title': title,
#               'forms':lforms,
#               'id': procedure_id,
#               'schedule': p.schedule,
#               'fileset': p.fileset}
#     if request.method == "POST":
#         data = copy(request.POST)
#         if data['procedure-schedule'] == u"":
#             data['procedure-schedule'] = u"%d" % p.schedule.id
#         if data['procedure-fileset'] == u"":
#             data['procedure-fileset'] = u"%d" % p.fileset.id
#         procedure_form = ProcedureEditForm(data, instance=p, prefix="procedure")
#         if procedure_form.is_valid():
#             procedure_form.save()
#             messages.success(request, "Procedimento alterado com sucesso")
#             return redirect('/procedures/list')
#         else:
#             messages.error(request, "O procedimento de backup não foi criado devido aos seguintes erros")
#             content['forms'] = [procedure_form]
#             return render_to_response(request, "edit_procedure.html", content)
#     return render_to_response(request, 'edit_procedure.html', content)


def edit(request, object_id):
    s = get_object_or_404(Schedule, pk=object_id)
    print s.if_week()
    schedule_form = forms.ScheduleForm(prefix="schedule", instance=s)
    month_form = forms.MonthForm(prefix="month", instance=s.if_month())
    week_form = forms.WeekForm(prefix="week", instance=s.if_week())
    day_form = forms.DayForm(prefix="day", instance=s.if_day())
    hour_form = forms.HourForm(prefix="hour", instance=s.if_hour())
    days_range = range(1, 32)
    weekdays_range = {0:'Domingo', 1:'Segunda-feira', 2:'Terça-feira',
                      3:'Quarta-feira', 4:'Quinta-feira', 5:'Sexta-feira',
                      6:'Sabado'}
    end_days_range = [5, 10, 15, 20, 25, 30]
    content = {'title':u'Criar Agendamento',
               'schedule_form':schedule_form,
               'month_form': month_form,
               'week_form': week_form,
               'day_form': day_form,
               'hour_form': hour_form,
               'days':days_range,
               'end_days':end_days_range,
               'weekdays':weekdays_range,
               'messages':[]
              }
    return render_to_response(request, 'add_schedule.html', content)


def edit___(request, procedure_id):
    p = get_object_or_404(Procedure, pk=procedure_id)
    title = u"Editando '%s'" % p.name
    partial_form = ProcedureEditForm(prefix="procedure", instance=p)
    lforms = [partial_form]
    content = {'title': title,
              'forms':lforms,
              'id': procedure_id,
              'schedule': p.schedule,
              'fileset': p.fileset}
    if request.method == "POST":
        data = copy(request.POST)
        if data['procedure-schedule'] == u"":
            data['procedure-schedule'] = u"%d" % p.schedule.id
        if data['procedure-fileset'] == u"":
            data['procedure-fileset'] = u"%d" % p.fileset.id
        procedure_form = ProcedureEditForm(data, instance=p, prefix="procedure")
        if procedure_form.is_valid():
            procedure_form.save()
            messages.success(request, "Procedimento '%s' alterado com sucesso" % p.name)
            return redirect('/procedures/list')
        else:
            messages.error(request, "O procedimento de backup não foi criado devido aos seguintes erros")
            content['forms'] = [procedure_form]
            return render_to_response(request, "edit_procedure.html", content)
    return render_to_response(request, 'edit_procedure.html', content)


def add_schedule(request):
    schedule_form = forms.ScheduleForm(prefix="schedule")
    month_form = forms.MonthForm(prefix="month")
    week_form = forms.WeekForm(prefix="week")
    day_form = forms.DayForm(prefix="day")
    hour_form = forms.HourForm(prefix="hour")
    days_range = range(1, 32)
    weekdays_range = {0:'Domingo', 1:'Segunda-feira', 2:'Terça-feira',
                      3:'Quarta-feira', 4:'Quinta-feira', 5:'Sexta-feira',
                      6:'Sabado'}
    end_days_range = [5, 10, 15, 20, 25, 30]
    content = {'title':u'Criar Agendamento',
               'schedule_form':schedule_form,
               'month_form': month_form,
               'week_form': week_form,
               'day_form': day_form,
               'hour_form': hour_form,
               'days':days_range,
               'end_days':end_days_range,
               'weekdays':weekdays_range,
               'messages':[]
              }
    if request.method == "POST":
        print request.POST
        data = copy(request.POST)
        schedule_form = forms.ScheduleForm(data, prefix='schedule')
        content['schedule_form'] = schedule_form
        month_form = forms.MonthForm(data, prefix='month')
        content['month_form'] = month_form
        week_form = forms.WeekForm(data, prefix='week')
        content['week_form'] = week_form
        day_form = forms.DayForm(data, prefix='day')
        content['day_form'] = day_form
        hour_form = forms.HourForm(data, prefix='hour')
        content['hour_form'] = hour_form
        
        if any([data.has_key("%s-active" % data_key) for data_key in ['month', 'week', 'day', 'hour']]):
            if schedule_form.is_valid():
                schedule = schedule_form.save()
                for data_key in ['month', 'week', 'day', 'hour']:
                    data['%s-schedule' % data_key] = schedule.id
                to_validate_forms = []
                if data.has_key('month-active'):
                    month_form = forms.MonthForm(data, prefix='month')
                    to_validate_forms.append(month_form)
                if data.has_key('week-active'):
                    week_form = forms.WeekForm(data, prefix='week')
                    to_validate_forms.append(week_form)
                if data.has_key('day-active'):
                    day_form = forms.DayForm(data, prefix='day')
                    to_validate_forms.append(day_form)
                if data.has_key('hour-active'):
                    hour_form = forms.HourForm(data, prefix='hour')
                    to_validate_forms.append(hour_form)
                if all([f.is_valid() for f in to_validate_forms]):
                    [f.save() for f in to_validate_forms]
                    content['messages'] = [u"Agendamento '%s' criado com sucesso" % schedule.name]
                else:
                    schedule.delete()
                    content['messages'] = [u"Nenhum agendamento foi criado"]
        else:
            content['messages'] = ["Nenhum agendamento foi selecionado"]
    return render_to_response(request, "add_schedule.html", content)


# def add_schedule(request):
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
#                'weekdays':weekdays_range,
#                'messages':[u'Mensagem teste',
#                            u'Mensagem teste 2']
#               }
#     if request.method == "POST":
#         print request.POST
#         data = request.POST
#         new_schedule = insert_schedule(data)
#         messages = []
#         messages.append("bla")
#         messages.append("ble")
#         messages.append("bli")
#         content["messages"] = messages
#         if new_schedule:
#             messages = []
#             messages.append(insert_monthly(data, new_schedule))
#             messages.append(insert_weekly(data, new_schedule))
#             messages.append(insert_daily(data, new_schedule))
#             messages.append(insert_hourly(data, new_schedule))
#             content["messages"] = messages
#     return render_to_response("add_schedule.html", content)


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