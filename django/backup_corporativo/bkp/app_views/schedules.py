#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.views import global_vars, authentication_required
from backup_corporativo.bkp.forms import MonthlyTriggerForm, WeeklyTriggerForm

### Schedule ###

@authentication_required
def delete_schedule(request, sched_id):
    E.update(request)
    
    if request.method == 'GET':
        E.sched = get_object_or_404(Schedule, pk=sched_id)
        E.proc = E.sched.procedure
        E.comp = E.proc.computer
        E.msg = _("Are you sure?")
        E.template = 'bkp/schedule/delete_schedule.html'
        return E.render()
    elif request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=sched_id)
        proc = sched.procedure
        sched.delete()
        E.msg = _("Schedule was successfully removed.")
        location = reverse("edit_backup", args=[proc.id])
        return HttpResponseRedirect(location)


@authentication_required
def edit_schedule(request, sched_id):
    E.update(request)
    
    if request.method == 'GET':
        E.sched = get_object_or_404(Schedule, pk=sched_id)
        E.proc = E.sched.procedure
        E.comp = E.proc.computer
        E.trig = E.sched.get_trigger()
        cmd = "E.triggform = %sTriggerForm(instance=E.trig)" % E.sched.type
        exec(cmd)
        E.template = 'bkp/schedule/edit_schedule.html'
        return E.render()


@authentication_required
def update_schedule(request, sched_id):
    E.update(request)
    
    if request.method == 'POST':
        E.sched = get_object_or_404(Schedule, pk=sched_id)
        E.proc = E.sched.procedure
        E.comp = E.proc.computer
        E.trig = E.sched.get_trigger()
        cmd = "E.triggform = %sTriggerForm(request.POST, instance=E.trig)"
        cmd = cmd % E.sched.type
        exec(cmd)
        if E.triggform.is_valid():
            E.triggform.save()
            E.msg = _("Schedule was successfully updated.")
            location = reverse("edit_backup", args=[E.proc.id])
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/schedule/edit_schedule.html'
            return E.render()