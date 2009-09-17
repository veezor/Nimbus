#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Schedule, Computer, Procedure, WeeklyTrigger, MonthlyTrigger
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Schedule ###

@authentication_required
def edit_schedule(request, sched_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'GET':
        vars_dict['sched'] = get_object_or_404(Schedule, pk=sched_id)
        vars_dict['proc'] = vars_dict['sched'].procedure
        vars_dict['comp'] = vars_dict['proc'].computer
        vars_dict['trigg'] = vars_dict['sched'].get_trigger()
        triggclass = globals()["%sTriggerForm" % vars_dict['sched'].type]
        forms_dict['triggform'] = triggclass(instance=vars_dict['trigg'])
        forms_dict['schedauxform'] = ScheduleAuxForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/schedule/edit_schedule.html',
            return_dict,
            context_instance=RequestContext(request))

def update_schedule(request, sched_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'POST':
        vars_dict['sched'] = get_object_or_404(Schedule, pk=sched_id)
        vars_dict['proc'] = vars_dict['sched'].procedure
        vars_dict['comp'] = vars_dict['proc'].computer
        vars_dict['trigg'] = vars_dict['sched'].get_trigger()
        triggclass = globals()["%sTriggerForm" % vars_dict['sched'].type]
        forms_dict['triggform'] = triggclass(
            request.POST,
            instance=vars_dict['trigg'])
        if forms_dict['triggform'].is_valid():
            forms_dict['triggform'].save()
            request.user.message_set.create(
                message="Agendamento foi alterado com sucesso.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            request.user.message_set.create(
                message="Existem erros e o agendamento não foi alterado.")
            return_dict = utils.merge_dicts(
                return_dict,
                forms_dict,
                vars_dict)
            return render_to_response(
                'bkp/schedule/edit_schedule.html',
                return_dict,
                context_instance=RequestContext(request))



@authentication_required
def delete_schedule(request, sched_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['sched'] = get_object_or_404(Schedule, pk=sched_id)
        vars_dict['proc'] = vars_dict['sched'].procedure
        vars_dict['comp'] = vars_dict['proc'].computer
        request.user.message_set.create(
            message="Confirme a remoção do agendamento.")
        return_dict = utils.merge_dicts(
            return_dict,
            forms_dict,
            vars_dict)
        return render_to_response(
            'bkp/schedule/delete_schedule.html',
            return_dict,
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        sched = get_object_or_404(Schedule, pk=sched_id)
        sched.delete()
        request.user.message_set.create(
            message="Agendamento foi removido permanentemente.")
        return redirect_back_or_default(
            request,
            default=computer_path(request, computer_id))
