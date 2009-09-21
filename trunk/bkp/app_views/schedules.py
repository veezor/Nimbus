#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Schedule ###

@authentication_required
def delete_schedule(request, sched_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['sched'] = get_object_or_404(Schedule, pk=sched_id)
        vars_dict['proc'] = vars_dict['sched'].procedure
        vars_dict['comp'] = vars_dict['proc'].computer
        request.user.message_set.create(
            message="Confirme a remoção do agendamento.")
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/schedule/delete_schedule.html',
            return_dict,
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=sched_id)
        computer_id = sched.procedure.computer.id
        sched.delete()
        request.user.message_set.create(
            message="Agendamento foi removido permanentemente.")
        location = utils.computer_path(request, computer_id)
        return redirect_back(request, default=location)