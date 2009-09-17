#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, Procedure
from backup_corporativo.bkp.forms import ProcedureForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Procedure ###
@authentication_required
def edit_procedure(request, proc_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
    vars_dict['comp'] = vars_dict['proc'].computer
    
    if request.method == 'GET':
        forms_dict['procform'] = ProcedureForm(
            instance=vars_dict['proc'])
        return_dict = utils.merge_dicts(
            return_dict,
            forms_dict,
            vars_dict)
        return render_to_response(
            'bkp/procedure/edit_procedure.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_procedure(request, proc_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
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
            return HttpResponseRedirect(
                utils.edit_path("procedure", proc_id, request))
        else:
            return_dict = utils.merge_dicts(
                return_dict,
                forms_dict,
                vars_dict)
            request.user.message_set.create(
                message="Existem erros e o procedimento não foi alterado.")
            return render_to_response(
                'bkp/procedure/edit_procedure.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def delete_procedure(request, proc_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'GET': 
        vars_dict['proc'] = get_object_or_404(Procedure, pk=proc_id)
        vars_dict['comp'] = vars_dict['proc'].computer
        request.user.message_set.create(
            message="Confirme a remoção do procedimento.")
        return_dict = utils.merge_dicts(
            return_dict,
            forms_dict,
            vars_dict)
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
        return HttpResponseRedirect(
            utils.path("computer", comp.id,request))