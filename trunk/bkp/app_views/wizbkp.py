#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
from backup_corporativo.bkp.models import Computer, Procedure, Storage, FileSet, Schedule, MonthlyTrigger, WeeklyTrigger
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, ScheduleAuxForm, ScheduleForm, WeeklyTriggerForm, MonthlyTriggerForm, FileSetForm
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

###               ###
#   Código Novo     #
###               ###

@authentication_required
def new_backup(request, comp_id=None, proc_id=None):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}
    if comp_id is not None:
        vars_dict['comp'] = get_object_or_404(Computer, pk=comp_id)
    if proc_id is not None:
        vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
    if request.method == 'GET':
        vars_dict['backup_step'] = __backup_step(comp_id, proc_id)
        
        if vars_dict['backup_step'] == 1:
            forms_dict['compform'] = ComputerForm()
        elif vars_dict['backup_step'] == 2:
            forms_dict['procform'] = ProcedureForm()
            forms_dict['fsetform'] = FileSetForm()
        elif vars_dict['backup_step'] == 3:
            forms_dict['schedform'] = ScheduleForm()
            forms_dict['wtriggform'] = WeeklyTriggerForm()
            forms_dict['mtriggform'] = MonthlyTriggerForm()

        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/wizard/computer/computer_wizard.html',
            return_dict,
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        vars_dict['backup_step'] = __backup_step(comp_id, proc_id)
        if vars_dict['backup_step'] == 1:
            forms_dict['compform'] = ComputerForm(request.POST)
            if forms_dict['compform'].is_valid():
                comp = forms_dict['compform'].save()
                return HttpResponseRedirect(
                    utils.backup_computer_path(request, comp.id))
            else:
                return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response(
                    'bkp/wizard/computer/computer_wizard.html',
                    return_dict,
                    context_instance=RequestContext(request))
        elif vars_dict['backup_step'] == 2:
            forms_dict['procform'] = ProcedureForm(request.POST)
            forms_dict['fsetform'] = FileSetForm(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_list]):
                proc = forms_dict['procform'].save(commit=False)
                fset = forms_dict['fsetform'].save(commit=False)
                proc.computer_id = comp_id
                proc.save()
                fset.procedure_id = proc.id
                fset.save()
                return HttpResponseRedirect(
                    utils.backup_procedure_path(request, comp_id, proc.id))
            else:
                return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response(
                    'bkp/wizard/computer/computer_wizard.html',
                    return_dict,
                    context_instance=RequestContext(request))
        elif vars_dict['backup_step'] == 3:
            # TODO: Tratar formulário semanal
            forms_dict['schedform'] = ScheduleForm({'type':'Monthly'})
            forms_dict['mtriggform'] = MonthlyTriggerForm(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_list]):
                sched = forms_dict['schedform'].save(commit=False)
                mtrigg = forms_dict['mtriggform'].save(commit=False)
                sched.procedure_id = proc_id
                sched.save()
                mtrigg.schedule_id = sched.id
                mtrigg.save()
                return HttpResponseRedirect(
                    utils.path("computer", comp_id, request))
            else:
                return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response('bkp/wizard/computer/computer_wizard.html', return_dict, context_instance=RequestContext(request))

def __backup_step(comp_id=None ,proc_id=None, job_id=None):
    if all([arg is None for arg in [comp_id,proc_id]]):
        return 1
    elif all([arg is None for arg in [proc_id]]):
        return 2
    elif all([arg is not None for arg in [comp_id,proc_id]]):
        return 3
    return -1 # Função nunca deverá chegar aqui.
