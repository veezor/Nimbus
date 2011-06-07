# Create your views here.
# -*- coding: UTF-8 -*-

import traceback
import simplejson
import socket
from copy import copy

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib import messages

from nimbus.computers.models import Computer
from nimbus.schedules import forms
from nimbus.shared.enums import levels, days_range, weekdays_range, end_days_range
from nimbus.shared.views import render_to_response
from nimbus.schedules.models import Schedule
from nimbus.procedures.models import Procedure
from nimbus.procedures.views import resume_add as procedure_view_resume_add

@login_required
def edit(request, object_id):
    s = get_object_or_404(Schedule, pk=object_id)
    procedures = Procedure.objects.filter(schedule=s.id)
    month_instance = s.if_month()
    week_instance = s.if_week()
    day_instance = s.if_day()
    hour_instance = s.if_hour()
    schedule_form = forms.ScheduleForm(prefix="schedule", instance=s)
    month_form = forms.MonthForm(prefix="month", instance=month_instance)
    week_form = forms.WeekForm(prefix="week", instance=week_instance)
    day_form = forms.DayForm(prefix="day", instance=day_instance)
    hour_form = forms.HourForm(prefix="hour", instance=hour_instance)
    days_range = range(1, 32)
    weekdays_range = {0:'Domingo', 1:'Segunda-feira', 2:'Terça-feira',
                      3:'Quarta-feira', 4:'Quinta-feira', 5:'Sexta-feira',
                      6:'Sabado'}
    end_days_range = [5, 10, 15, 20, 25, 30]
    content = {'title':u"Alterando agendamento '%s'" % s.name,
               'schedule_form':schedule_form,
               'month_form': month_form,
               'week_form': week_form,
               'day_form': day_form,
               'hour_form': hour_form,
               'days':days_range,
               'end_days':end_days_range,
               'weekdays':weekdays_range,
               'schedule': s,
               'month': month_instance,
               'week': week_instance,
               'day': day_instance,
               'hour': hour_instance,
               'procedures': procedures,
               'messages':[]}
    if request.method == "POST":
        print request.POST
        data = copy(request.POST)
        for data_key in ['month', 'week', 'day', 'hour']:
            data['%s-schedule' % data_key] = s.id
        schedule_form = forms.ScheduleForm(data, prefix="schedule", instance=s)
        month_form = forms.MonthForm(data, prefix="month", instance=month_instance)
        week_form = forms.WeekForm(data, prefix="week", instance=week_instance)
        day_form = forms.DayForm(data, prefix="day", instance=day_instance)
        hour_form = forms.HourForm(data, prefix="hour", instance=hour_instance)
        content['schedule_form'] = schedule_form
        content['month_form'] = month_form
        content['week_form'] = week_form
        content['day_form'] = day_form
        content['hour_form'] = hour_form
        if any([data.has_key("%s-active" % data_key) for data_key in ['month',
                                                      'week', 'day', 'hour']]):
            to_validate_forms = []
            to_remove_forms = []
            to_validate_forms.append(schedule_form)
            if data.has_key('month-active'):
                to_validate_forms.append(month_form)
            elif month_instance:
                to_remove_forms.append(s.month)
            if data.has_key('week-active'):
                to_validate_forms.append(week_form)
            elif week_instance:
                to_remove_forms.append(s.week)
            if data.has_key('day-active'):
                to_validate_forms.append(day_form)
            elif day_instance:
                to_remove_forms.append(s.day)
            if data.has_key('hour-active'):
                to_validate_forms.append(hour_form)
            elif hour_instance:
                to_remove_forms.append(s.hour)
            print [f.is_valid() for f in to_validate_forms]
            if all([f.is_valid() for f in to_validate_forms]):
                [f.delete() for f in to_remove_forms]
                [f.save() for f in to_validate_forms]
                content['messages'] = [u"Agendamento '%s' alterado com sucesso" % s.name]
            else:
                print [(f, f.errors) for f in to_validate_forms]
                content['messages'] = [u"Nenhum agendamento foi criado"]
        else:
            content['messages'] = ["Nenhum agendamento foi selecionado"]
    content['schedule_form'].fields['is_model'].widget.attrs['disabled'] = "disabled"
    return render_to_response(request, "edit_schedule.html", content)

@login_required
def add_schedule(request):
    if request.method == "POST":
        print request.POST
        data = copy(request.POST)
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
                   'days': days_range,
                   'end_days': end_days_range,
                   'weekdays': weekdays_range,
                   'computer_id': data['computer_id'],
                   'fileset_id': data['fileset_id'],
                   'storage_id': data['storage_id'],
                   'procedure_name': data['procedure_name'],
                   'retention_time': data['retention_time'],
                   'messages':[]}
        if not data.has_key('first_step'):
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
                        messages.success(request, "Agendamento '%s' criado" % schedule.name)
                        return redirect("/procedures/resume/%s/%s/%s/%s/%s/%s/" % 
                                        (data['computer_id'],
                                         schedule.id,
                                         data['fileset_id'],
                                         data['storage_id'],
                                         data['retention_time'],
                                         data['procedure_name']))
                        # content['messages'] = [u"Agendamento '%s' criado com sucesso" % schedule.name]
                    else:
                        schedule.delete()
                        content['messages'] = [u"Nenhum agendamento foi criado"]
            else:
                content['messages'] = ["Nenhum agendamento foi selecionado"]
    return render_to_response(request, "add_schedule.html", content)
