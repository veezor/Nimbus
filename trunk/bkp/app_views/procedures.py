#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.forms import ProcedureForm
from backup_corporativo.bkp.forms import MonthlyTriggerForm
from backup_corporativo.bkp.forms import WeeklyTriggerForm
from backup_corporativo.bkp.forms import FileSetForm
from backup_corporativo.bkp.forms import ScheduleForm
from backup_corporativo.bkp.forms import ProcedureAuxForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Procedure ###
@authentication_required
def edit_procedure(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)

    if request.method == 'GET':
        forms_dict['procform'] = ProcedureForm(instance=vars_dict['proc'])
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def update_procedure(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)

    if request.method == 'POST':
        forms_dict['procform'] = ProcedureForm(request.POST,instance=vars_dict['proc'])
        
        if forms_dict['procform'].is_valid():
            forms_dict['procform'].save()
            request.user.message_set.create(message="O procedimento foi alterado com sucesso.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o procedimento não foi alterado.")
            return render_to_response('bkp/edit_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def new_procedure(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    forms_dict['procform'] = ProcedureForm()
    forms_dict['schedform'] = ScheduleForm()
    forms_dict['fsetform'] = FileSetForm()
    forms_dict['triggform'] = MonthlyTriggerForm()
    forms_dict['mtriggform'] = WeeklyTriggerForm()
    forms_dict['procauxform'] = ProcedureAuxForm()

    if request.method == 'GET':
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_procedure(request, computer_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        temp_dict['procauxform'] = ProcedureAuxForm(request.POST)

        if temp_dict['procauxform'].is_valid():
            forms_dict['procform'] = ProcedureForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['FileSet']:
                forms_dict['fsetform'] = FileSetForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['Schedule']:
                forms_dict['schedform'] = ScheduleForm(request.POST)
            if temp_dict['procauxform'].cleaned_data['Trigger']:
                triggclass = globals()["%sTriggerForm" % temp_dict['procauxform'].cleaned_data['schedule_type']]
                forms_dict['triggform'] = triggclass(request.POST)
            forms_list = forms_dict.values()
            if all([form.is_valid() for form in forms_dict.values()]):
                proc = forms_dict['procform'].save(commit=False)
                fset = forms_dict['fsetform'].save(commit=False)
                sched = forms_dict['schedform'].save(commit=False)
                trigg = forms_dict['triggform'].save(commit=False)
                proc.computer_id = computer_id
                proc.save()
                proc.build_backup(fset, sched, trigg)
                request.user.message_set.create(message="Procedimento cadastrado com sucesso.")
                return HttpResponseRedirect(computer_path(request, computer_id))
            else:
                # Load forms and vars
                vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
                request.user.message_set.create(message="Existem erros e o procedimento não foi cadastrado.")
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
                return render_to_response('bkp/new_procedure.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def delete_procedure(request, computer_id, procedure_id):
    if request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=procedure_id)
        proc.delete()
        request.user.message_set.create(message="Procedimento removido permanentemente.")
        return redirect_back_or_default(request, default=computer_path(request, computer_id))
        

