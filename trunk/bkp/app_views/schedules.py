#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.forms import ScheduleForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Schedule ###
@authentication_required
def view_schedule(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
        vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
        vars_dict['fsets'] = vars_dict['proc'].filesets_list()
        
        # TODO: optmize following chunk of code
        if (vars_dict['sched'].type == 'Weekly'):
            try:
                vars_dict['trigger'] = WeeklyTrigger.objects.get(schedule=vars_dict['sched'])
                forms_dict['triggerform'] = WeeklyTriggerForm(instance=vars_dict['trigger'])
                vars_dict['triggerformempty'] = False
            except WeeklyTrigger.DoesNotExist:
                forms_dict['triggerform'] = WeeklyTriggerForm()
                vars_dict['triggerformempty'] = True
        elif (vars_dict['sched'].type == 'Monthly'):
            try:
                vars_dict['trigger'] = MonthlyTrigger.objects.get(schedule=vars_dict['sched'])
                forms_dict['triggerform'] = MonthlyTriggerForm(instance=vars_dict['trigger'])                
                vars_dict['triggerformempty'] = False
            except MonthlyTrigger.DoesNotExist:
                forms_dict['triggerform'] = MonthlyTriggerForm()                
                vars_dict['triggerformempty'] = True
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))       


@authentication_required
def create_schedule(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'POST':
        forms_dict['schedform'] = ScheduleForm(request.POST)
        
        if forms_dict['schedform'].is_valid():
            schedule = Schedule()
            schedule.procedure_id = procedure_id
            schedule.type = forms_dict['schedform'].cleaned_data['type']
            schedule.save()
            request.user.message_set.create(message="Agendamento cadastrado com sucesso.")
            return HttpResponseRedirect(schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = vars_dict['comp'].procedures_list()
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['scheds'] = vars_dict['proc'].schedules_list()
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi cadastrado.")
            return render_to_response('bkp/view_procedure.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def delete_schedule(request, computer_id, procedure_id, schedule_id):
    if request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=schedule_id)
        sched.delete()
        request.user.message_set.create(message="Agendamento foi removido permanentemente.")
        return redirect_back_or_default(request, default=procedure_path(request, computer_id,procedure_id))
