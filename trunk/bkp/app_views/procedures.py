#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, Procedure, Schedule
from backup_corporativo.bkp.forms import ProcedureForm, MonthlyTriggerForm, WeeklyTriggerForm, ScheduleAuxForm, WizardAuxForm
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Procedure ###
@authentication_required
def edit_procedure(request, proc_id):
    vars_dict, forms_dict = global_vars(request)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
    vars_dict['comp'] = vars_dict['proc'].computer
    if request.method == 'GET':
        forms_dict['procform'] = ProcedureForm(
            instance=vars_dict['proc'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/procedure/edit_procedure.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_procedure(request, proc_id):
    vars_dict, forms_dict = global_vars(request)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
    vars_dict['comp'] = vars_dict['proc'].computer
    if request.method == 'POST':
        forms_dict['procform'] = ProcedureForm(
            request.POST,
            instance=vars_dict['proc'])
        if forms_dict['procform'].is_valid():
            forms_dict['procform'].save()
            request.user.message_set.create(
                message="O procedimento foi alterado com sucesso.")
            location = utils.edit_path("procedure", proc_id, request)
            return HttpResponseRedirect(location)
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            request.user.message_set.create(
                message="Existem erros e o procedimento não foi alterado.")
            return render_to_response(
                'bkp/procedure/edit_procedure.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def delete_procedure(request, proc_id):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'GET': 
        vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
        vars_dict['comp'] = vars_dict['proc'].computer
        request.user.message_set.create(
            message="Confirme a remoção do procedimento.")
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/procedure/delete_procedure.html',
            return_dict,
            context_instance=RequestContext(request))
    #TODO: Separar em dois objetos de view
    elif request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=proc_id)
        comp = proc.computer
        proc.delete()
        request.user.message_set.create(
            message="Procedimento removido permanentemente.")
        location = utils.path("computer", comp.id,request)
        return HttpResponseRedirect(location)


@authentication_required
def new_procedure_schedule(request, proc_id):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'GET':
        type = request.GET['type']
        __ensure_valid_type(type)
        if 'wizard' in request.GET:
            vars_dict['wizard'] = request.GET['wizard']
        else:
            vars_dict['wizard'] = False
        vars_dict['sched_type'] = type
        vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
        vars_dict['comp'] = vars_dict['proc'].computer
        vars_dict['new_schedule_url'] = utils.new_procedure_schedule(
            vars_dict['proc'].id,
            request,
            type=utils.schedule_inverse(type),
            wizard=vars_dict['wizard'])
        triggform = "forms_dict['triggform'] = %sTriggerForm()" % type
        exec(triggform)
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/procedure/new_procedure_schedule.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def create_procedure_schedule(request, proc_id):
    if request.method == 'POST':
        vars_dict, forms_dict = global_vars(request)
        aux_dict = {}
        aux_dict['wizauxform'] = WizardAuxForm(request.POST)
        if aux_dict['wizauxform'].is_valid():
            wiz = aux_dict['wizauxform'].cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
        vars_dict['comp'] = vars_dict['proc'].computer
        forms_dict['sched_aux_form'] = ScheduleAuxForm(request.POST)
        if not(forms_dict['sched_aux_form'].is_valid()):
            raise Exception("Erro de programaçao: sched_aux_form malformado.")
        type = forms_dict['sched_aux_form'].cleaned_data['schedule_type']
        triggform = \
            "forms_dict['triggform'] = %sTriggerForm(request.POST)" % type
        exec(triggform)
        if forms_dict['triggform'].is_valid():
            sched = Schedule(type=type)
            sched.procedure = vars_dict['proc']
            sched.save()
            trigg = forms_dict['triggform'].save(commit=False)
            trigg.schedule = sched
            trigg.save()
            return HttpResponseRedirect(
                utils.path("computer", vars_dict['comp'].id, request))
        else:
            vars_dict['new_schedule_url'] = utils.new_procedure_schedule(
                vars_dict['proc'].id,
                request,
                type=utils.schedule_inverse(type),
                wizard=wiz)
            vars_dict['sched_type'] = type
            vars_dict['wizard'] = wiz
            return_dict = utils.merge_dicts(forms_dict, vars_dict, aux_dict)
            return render_to_response(
                'bkp/procedure/new_procedure_schedule.html',
                return_dict,
                context_instance=RequestContext(request))


#
# Definições auxiliares
#
def __ensure_valid_type(type):
    if type in ('Weekly','Monthly'):
        pass
    else:
        raise Exception("Erro de programação: tipo de agendamento inválido")
