#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from environment import ENV

#TODO: remover import do módulo utils
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Computer, Procedure, Schedule
from backup_corporativo.bkp.forms import ProcedureForm, MonthlyTriggerForm, WeeklyTriggerForm, ScheduleAuxForm, WizardAuxForm, FileSetForm
from backup_corporativo.bkp.views import global_vars, authentication_required, DAYS_OF_THE_WEEK


@authentication_required
def edit_backup(request, proc_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.proc.humanize()
        E.comp = E.proc.computer
        E.fsets = E.proc.fileset_set.all()
        E.scheds = E.proc.schedule_set.all()
        E.DAYS_OF_THE_WEEK = DAYS_OF_THE_WEEK
        E.procform = ProcedureForm(instance=E.proc)
        E.template = 'bkp/procedure/edit_backup.html'
        return E.render()


@authentication_required
def update_backup(request, proc_id):
    E = ENV(request)
    E.proc = get_object_or_404(Procedure, pk=proc_id)
    E.comp = E.proc.computer
    if request.method == 'POST':
        E.procform = ProcedureForm(request.POST, instance=E.proc)
        if E.procform.is_valid():
            E.procform.save()
            E.msg = u"Backup foi alterado com sucesso."
            location = reverse("edit_backup", args=[proc_id])
            return HttpResponseRedirect(location)
        else:
            E.msg = u"Erro ao alterar backup."
            E.template = 'bkp/procedure/edit_backup.html'
            return E.render()


@authentication_required
def delete_procedure(request, proc_id):
    E = ENV(request)

    if request.method == 'GET':
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.template = 'bkp/procedure/delete_procedure.html'
        return E.render()
    elif request.method == 'POST':
        proc = get_object_or_404(Procedure, pk=proc_id)
        comp = proc.computer
        proc.delete()
        E.msg = u"Backup foi removido permanentemente."
        location = reverse("view_computer", args=[comp.id])
        return HttpResponseRedirect(location)


@authentication_required
def new_procedure_fileset(request, proc_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.fsetform = FileSetForm()
        E.template = 'bkp/procedure/new_procedure_fileset.html'
        return E.render()


@authentication_required
def create_procedure_fileset(request, proc_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        E.fsetform = FileSetForm(request.POST)
        if E.fsetform.is_valid():
            fset = E.fsetform.save(commit=False)
            fset.procedure = E.proc
            fset.save()
            location = reverse('edit_backup',args=[E.proc.id])
            return HttpResponseRedirect(location)
        else:
            E.msg = u"Erro ao adicionar local."
            E.template = 'bkp/procedure/new_procedure_fileset.html'
            return E.render()


@authentication_required
def new_procedure_schedule(request, proc_id):
    E = ENV(request)
    
    if request.method == 'GET':
        if 'type' in request.GET:
            E.sched_type = request.GET['type']
            __ensure_valid_type(E.sched_type)
        else:
            E.sched_type = 'Weekly'
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.comp = E.proc.computer
        # TODO: usar template tag filter url
        E.new_schedule_url = utils.new_procedure_schedule(
            E.proc.id,
            request,
            type=utils.schedule_inverse(E.sched_type),
            wizard=E.wizard
        )
        triggform = "E.triggform = %sTriggerForm()" % E.sched_type
        exec(triggform)
        E.template = 'bkp/procedure/new_procedure_schedule.html'
        return E.render()


@authentication_required
def create_procedure_schedule(request, proc_id):
    E = ENV(request)
    
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
            emsg = u"""Erro de programaçao. "sched_aux_form" malformado."""
            raise Exception(emsg)
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
            location = reverse("edit_backup", args=[proc_id])
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
        emsg = u"""Erro de programação: "schedule type" inválido. Tente "Weekly" ou "Monthly"."""
        raise Exception(emsg)
