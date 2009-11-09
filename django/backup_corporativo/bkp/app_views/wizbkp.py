#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _

from Environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.views import global_vars, authentication_required
from backup_corporativo.bkp.models import Computer, Procedure, Storage, FileSet, Schedule, MonthlyTrigger, WeeklyTrigger
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, ScheduleAuxForm, ScheduleForm, WeeklyTriggerForm, MonthlyTriggerForm, FileSetForm


@authentication_required
def new_backup(request, comp_id=None, proc_id=None):
    E.update(request)
    
    if comp_id is not None:
        E.comp = get_object_or_404(Computer, pk=comp_id)
    if proc_id is not None:
        E.proc = get_object_or_404(Procedure, pk=proc_id)
    if request.method == 'GET':
        E.backup_step = __backup_step(comp_id, proc_id)
        
        if E.backup_step == 1:
            E.compform = ComputerForm()
        elif E.backup_step == 2:
            E.procform = ProcedureForm()
            E.fsetform = FileSetForm()
        elif E.backup_step == 3:
            E.schedform = ScheduleForm()
            E.wtriggform = WeeklyTriggerForm()
            E.mtriggform = MonthlyTriggerForm()
        E.template = 'bkp/wizard/computer/computer_wizard.html'
        return E.render()
    elif request.method == 'POST':
        E.backup_step = __backup_step(comp_id, proc_id)
        if E.backup_step == 1:
            E.compform = ComputerForm(request.POST)
            if E.compform.is_valid():
                comp = E.compform.save()
                location = utils.backup_computer_path(request, comp.id)
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/computer/computer_wizard.html'
                return E.render()
        elif E.backup_step == 2:
            E.procform = ProcedureForm(request.POST)
            E.fsetform = FileSetForm(request.POST)
            forms_list = [E.procform, E.fsetform]
            if all([form.is_valid() for form in forms_list]):
                proc = E.procform.save(commit=False)
                fset = E.fsetform.save(commit=False)
                proc.computer_id = comp_id
                proc.save()
                fset.procedure_id = proc.id
                fset.save()
                location = utils.backup_procedure_path(request, comp_id, proc.id)
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/computer/computer_wizard.html'
                return E.render()
        elif E.backup_step == 3:
            # TODO: Tratar formulário semanal
            E.schedform = ScheduleForm({'type':'Monthly'})
            E.mtriggform = MonthlyTriggerForm(request.POST)
            forms_list = [E.schedform, E.mtriggform]
            if all([form.is_valid() for form in forms_list]):
                sched = E.schedform.save(commit=False)
                mtrigg = E.mtriggform.save(commit=False)
                sched.procedure_id = proc_id
                sched.save()
                mtrigg.schedule_id = sched.id
                mtrigg.save()
                location = utils.path("computer", comp_id, request)
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/computer/computer_wizard.html'
                return E.render()

def __backup_step(comp_id=None ,proc_id=None, job_id=None):
    if all([arg is None for arg in [comp_id,proc_id]]):
        return 1
    elif all([arg is None for arg in [proc_id]]):
        return 2
    elif all([arg is not None for arg in [comp_id,proc_id]]):
        return 3
    return -1 # Função nunca deverá chegar aqui.
