#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.forms import WeeklyTriggerForm
from backup_corporativo.bkp.models import MonthlyTrigger
from backup_corporativo.bkp.forms import MonthlyTriggerForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Triggers ###
@authentication_required
def weeklytrigger(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        forms_dict['triggerform'] = WeeklyTriggerForm(request.POST)
        
        if forms_dict['triggerform'].is_valid():
            try:
                wtrigger = WeeklyTrigger.objects.get(schedule=vars_dict['sched'])
            except WeeklyTrigger.DoesNotExist:
                wtrigger = WeeklyTrigger()
            wtrigger.schedule_id = schedule_id
            wtrigger.sunday = forms_dict['triggerform'].cleaned_data['sunday']
            wtrigger.monday = forms_dict['triggerform'].cleaned_data['monday']
            wtrigger.tuesday = forms_dict['triggerform'].cleaned_data['tuesday']
            wtrigger.wednesday = forms_dict['triggerform'].cleaned_data['wednesday']
            wtrigger.thursday = forms_dict['triggerform'].cleaned_data['thursday']
            wtrigger.friday = forms_dict['triggerform'].cleaned_data['friday']
            wtrigger.saturday = forms_dict['triggerform'].cleaned_data['saturday']
            wtrigger.hour = forms_dict['triggerform'].cleaned_data['hour']
            wtrigger.level = forms_dict['triggerform'].cleaned_data['level']
            wtrigger.save()
            request.user.message_set.create(message="Agendamento configurado com sucesso.")
            return HttpResponseRedirect(schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
            vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
            vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
            vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['triggerformempty'] = True
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi configurado.")
            return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))        


@authentication_required
def monthlytrigger(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
    
    if request.method == 'POST':
        forms_dict['triggerform'] = MonthlyTriggerForm(request.POST)
        
        if forms_dict['triggerform'].is_valid():
            try:
                mtrigger = MonthlyTrigger.objects.get(schedule=vars_dict['sched'])
            except MonthlyTrigger.DoesNotExist:
                mtrigger = MonthlyTrigger()
            mtrigger.schedule_id = schedule_id
            mtrigger.hour = forms_dict['triggerform'].cleaned_data['hour']
            mtrigger.level = forms_dict['triggerform'].cleaned_data['level']
            mtrigger.target_days = forms_dict['triggerform'].cleaned_data['target_days']
            mtrigger.save()
            request.user.message_set.create(message="Agendamento configurado com sucesso.")
            return HttpResponseRedirect(schedule_path(request, schedule_id, procedure_id, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            vars_dict['procs'] = Procedure.objects.filter(computer=vars_dict['comp'])
            vars_dict['sched_lower_type'] = vars_dict['sched'].type.lower()
            vars_dict['scheds'] = Schedule.objects.filter(procedure=vars_dict['proc'])
            vars_dict['fsets'] = vars_dict['proc'].filesets_list()
            vars_dict['triggerformempty'] = True
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o agendamento não foi configurado.")
            return render_to_response('bkp/view_schedule.html', return_dict, context_instance=RequestContext(request))                
