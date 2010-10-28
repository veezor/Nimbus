# -*- coding: utf-8 -*-

from time import strftime, strptime

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from nimbus.schedules.shared import trigger_class, trigger_map
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form
from nimbus.shared import utils
from nimbus.libs.db import Session

from django.contrib import messages
from django.template import RequestContext

from nimbus.shared.enums import days, weekdays, levels, operating_systems




@login_required
def edit(request, object_id):
    
    schedule = Schedule.objects.get(id=object_id)
    title = u"Editar agendamento"
    template = 'base_schedules.html'

    
    extra_content = {
        'days': days,
        'weekdays': weekdays,
        'levels': levels,
        'operating_systems': operating_systems,
    }
    extra_content.update(**locals())

    if request.method == "GET":
        return render_to_response(request, template, extra_content)


    if request.method == "POST":

        
        errors = {}
        extra_content["errors"] =  errors
        
        schedule = Schedule.objects.get(id=object_id)
        
        template = 'edit_schedules.html'
        schedule_name = request.POST.get('schedule.name')

        try:
            old_schedule = Schedule.objects.get(name=schedule_name)
        except Schedule.DoesNotExist, notexist:
            old_schedule = None

        if (not old_schedule is None) and old_schedule != schedule:
            errors["schedule_name"] = "Nome não disponível. Já existe um agendamento com este nome"


        with Session() as session:

            if schedule_name:

                schedule.name = schedule_name


                selected_a_trigger = False
                triggers = ["schedule.monthly", "schedule.dayly", "schedule.weekly", "schedule.hourly"]


                for trigger in triggers:

                    selected_a_trigger = True
                    is_trigger_edit = False

                    trigger_name = trigger[len("schedule."):]
                    Trigger = trigger_class[trigger_name]

                    old_triggers = [ t for t in schedule.get_triggers() if isinstance(t, Trigger) ]

                    if old_triggers:
                        is_trigger_edit = True

                    if not request.POST.get(trigger + '.active'):

                        for t in old_triggers:
                            t.delete()
                            session.delete(t)

                    else: # active

                        hour = request.POST.get(trigger + '.hour')
                        if not hour:
                            errors['schedule_hour'] = "Você deve informar a hora de execução do agendamento %s" % trigger_map[trigger_name]
                        else:
                            if Trigger is Hourly:
                                hour = strftime("%H:%M", strptime(hour, "%M"))

                            level = request.POST.get(trigger + '.level')

                            if not trigger_name in ["dayly", "hourly"]:
                                post_days = set(request.POST.getlist(trigger + '.day'))

                                if not post_days and not is_trigger_edit:
                                    errors['schedule_day'] = "Você deve selecionar um dia para a execução do agendamento %s"  % trigger_map[trigger_name]
                                else:
                                    old_days = set([ unicode(t.day) for t in old_triggers ])

                                    if len(old_days) != len(post_days):
                                        new_days = post_days - old_days
                                        remove_days =  old_days - post_days 

                                        for d in remove_days:
                                            t = Trigger.objects.get(day=d,schedule=schedule)
                                            t.delete()
                                            session.delete(t)

                                        for d  in new_days:
                                            Trigger.objects.create(day=d, 
                                                                   hour=hour,
                                                                   level=level, 
                                                                   schedule=schedule)
                            else:
                                try:
                                    trigger = Trigger.objects.get(schedule=schedule)
                                except Trigger.DoesNotExist, error:
                                    trigger = Trigger()
                                    trigger.schedule = schedule

                                trigger.hour = hour
                                trigger.level = level
                                session.add(trigger)
                                trigger.save()



                            is_trigger_edit = False

                if not selected_a_trigger:
                    errors['schedule_name'] = "Você deve ativar pelo menos um tipo de agendamento"

            else:
                errors['schedule_name'] = "Você deve inserir um nome na configuração do agendamento"

            if not errors:
                schedule.save()
                session.add(schedule)
                messages.success(request, u"Agendamento atualizado com sucesso.")
                return redirect('nimbus.schedules.views.edit', object_id)
            else:
                session.rollback()
                extra_content.update(**locals())
                extra_content.update( utils.dict_from_querydict(
                                            request.POST,
                                            lists=("schedule_monthly_day",
                                                   "schedule_dayly_day",
                                                   "schedule_hourly_day",
                                                   "schedule_weekly_day")) )

                return render_to_response(request, template, extra_content )
     


