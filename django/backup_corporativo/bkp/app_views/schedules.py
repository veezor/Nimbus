#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy()

from Environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.views import global_vars, authentication_required

### Schedule ###

@authentication_required
def delete_schedule(request, sched_id):
    E.update(request)
    
    if request.method == 'GET':
        E.sched = get_object_or_404(Schedule, pk=sched_id)
        E.proc = E.sched.procedure
        E.comp = E.proc.computer
        E.msg = _("Confirme a remoção do agendamento.")
        E.template = 'bkp/schedule/delete_schedule.html'
        return E.render()
    elif request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=sched_id)
        computer_id = sched.procedure.computer.id
        sched.delete()
        E.msg = _("Agendamento foi removido permanentemente.")
        location = utils.computer_path(request, computer_id)
        return redirect_back(request, default=location)