#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Schedule, Computer, Procedure, WeeklyTrigger, MonthlyTrigger
from backup_corporativo.bkp.forms import ScheduleForm, ComputerForm, ProcedureForm, WeeklyTriggerForm, MonthlyTriggerForm, ScheduleAuxForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Schedule ###
@authentication_required
def create_schedule(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}
    
    if request.method == 'POST':
        temp_dict['schedauxform'] = ScheduleAuxForm(request.POST, ScheduleAuxForm())
        if temp_dict['schedauxform'].is_valid():
            triggclass = temp_dict['schedauxform'].cleaned_data['schedule_type']
            if triggclass == 'Weekly':
                triggform = 'wtriggform'
            elif triggclass == 'Monthly':
                triggform = 'mtriggform'
            else:
                triggform = ''
        
            forms_dict['schedform'] = ScheduleForm(request.POST)
            forms_list = forms_dict.values()
            
            if triggclass.lower() == 'weekly':
                forms_dict['wtriggform'] = WeeklyTriggerForm(request.POST)
            elif triggclass.lower() == 'monthly':
                forms_dict['mtriggform'] = MonthlyTriggerForm(request.POST)
       
            if all([form.is_valid() for form in forms_list]):
                sched = forms_dict['schedform'].save(commit=False)
                trigg = forms_dict[triggform].save(commit=False)
                
                sched.procedure_id = procedure_id
                sched.save()
                sched.build_backup(trigg)
            
                request.user.message_set.create(message="Agendamento cadastrado com sucesso.")
                return HttpResponseRedirect(computer_path(request, computer_id))
            else:
                vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
                vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                request.user.message_set.create(message="Existem erros e o agendamento não foi cadastrado.")
                return render_to_response('bkp/new/new_schedule.html', return_dict, context_instance=RequestContext(request))
            
@authentication_required
def new_schedule(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        forms_dict['schedform'] = ScheduleForm()
        forms_dict['mtriggform'] = MonthlyTriggerForm()
        forms_dict['wtriggform'] = WeeklyTriggerForm()
        forms_dict['schedauxform'] = ScheduleAuxForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new/new_schedule.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def edit_schedule(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        vars_dict['trigg'] = vars_dict['sched'].get_trigger()
        triggclass = globals()["%sTriggerForm" % vars_dict['sched'].type]
        forms_dict['triggform'] = triggclass(instance=vars_dict['trigg'])
        forms_dict['schedauxform'] = ScheduleAuxForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_schedule.html', return_dict, context_instance=RequestContext(request))

def update_schedule(request, computer_id, procedure_id, schedule_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'POST':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        vars_dict['trigg'] = vars_dict['sched'].get_trigger()
        triggclass = globals()["%sTriggerForm" % vars_dict['sched'].type]
        forms_dict['triggform'] = triggclass(request.POST, instance=vars_dict['trigg'])

        if forms_dict['triggform'].is_valid():
            forms_dict['triggform'].save()
            request.user.message_set.create(message="Agendamento foi alterado com sucesso.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            request.user.message_set.create(message="Existem erros e o agendamento não foi alterado.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/edit/edit_schedule.html', return_dict, context_instance=RequestContext(request))
            


@authentication_required
def delete_schedule(request, computer_id, procedure_id, schedule_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        vars_dict['sched'] = get_object_or_404(Schedule, pk=schedule_id)
        request.user.message_set.create(message="Confirme a remoção do agendamento.")
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/delete/delete_schedule.html', return_dict, context_instance=RequestContext(request))

    
    elif request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=schedule_id)
        sched.delete()
        request.user.message_set.create(message="Agendamento foi removido permanentemente.")
        return redirect_back_or_default(request, default=computer_path(request, computer_id))
