#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, Procedure, Schedule
from backup_corporativo.bkp.forms import ProcedureForm, MonthlyTriggerForm, WeeklyTriggerForm, ScheduleAuxForm, WizardAuxForm
from backup_corporativo.bkp.views import global_vars, authentication_required


@authentication_required
def edit_procedure(request, proc_id):
    E.update(request)
    E.proc = get_object_or_404(Procedure, pk=proc_id)
    E.comp = E.proc.computer
    if request.method == 'GET':
        E.procform = ProcedureForm(instance=E.proc)
        E.template = 'bkp/procedure/edit_procedure.html'
        return E.render()


@authentication_required
def update_procedure(request, proc_id):
    E.update(request)
    E.proc = get_object_or_404(Procedure, pk=proc_id)
    E.comp = E.proc.computer
    if request.method == 'POST':
        E.procform = ProcedureForm(request.POST, instance=E.proc)
        if E.procform.is_valid():
            E.procform.save()
            E.msg = _("Backup successfully updated.")
            location = utils.edit_path("procedure", proc_id, request)
            return HttpResponseRedirect(location)
        else:
            E.msg = _("Error at backup update.")
            E.template = 'bkp/procedure/edit_procedure.html'
            return E.render()


@authentication_required
def delete_procedure(request, proc_id):
    E.update(request)

    if request.method == 'GET':
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.msg = _("Do you really want to remove the Backup?")
        E.template = 'bkp/procedure/delete_procedure.html'
        return E.render()
    elif request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=proc_id)
        comp = proc.computer
        proc.delete()
        E.msg = _("Backup successfully removed.")
        location = utils.path("computer", comp.id,request)
        return HttpResponseRedirect(location)


@authentication_required
def new_procedure_schedule(request, proc_id):
    E.update(request)
    
    if request.method == 'GET':
        type = request.GET['type']
        __ensure_valid_type(type)
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.sched_type = type
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.new_schedule_url = utils.new_procedure_schedule(
            E.proc.id,
            request,
            type=utils.schedule_inverse(type),
            wizard=E.wizard
        )
        triggform = "E.triggform = %sTriggerForm()" % type
        exec(triggform)
        E.template = 'bkp/procedure/new_procedure_schedule.html'
        return E.render()


@authentication_required
def create_procedure_schedule(request, proc_id):
    E.update(request)
    
    if request.method == 'POST':
        
        
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            wiz = E.wizauxform.cleaned_data['wizard']
        else:
            wiz = False
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.sched_aux_form = ScheduleAuxForm(request.POST)
        if not E.sched_aux_form.is_valid():
            raise Exception("Erro de programaçao: sched_aux_form malformado.")
        type = E.sched_aux_form.cleaned_data['schedule_type']
        triggform = "E.triggform = %sTriggerForm(request.POST)" % type
        exec(triggform)
        if E.triggform.is_valid():
            sched = Schedule(type=type)
            sched.procedure = E.proc
            sched.save()
            trigg = E.triggform.save(commit=False)
            trigg.schedule = sched
            trigg.save()
            location = utils.path("computer", E.comp.id, request)
            return HttpResponseRedirect(location)
        else:
            E.new_schedule_url = utils.new_procedure_schedule(
                E.proc.id,
                request,
                type=utils.schedule_inverse(type),
                wizard=wiz
            )
            E.sched_type = type
            E.wizard = wiz
            E.template = 'bkp/procedure/new_procedure_schedule.html'
            return E.render()


#
# Definições auxiliares
#
def __ensure_valid_type(type):
    if type in ('Weekly','Monthly'):
        pass
    else:
        raise Exception("Erro de programação: tipo de agendamento inválido")
