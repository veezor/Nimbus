#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import FileSet, Computer, Procedure
from backup_corporativo.bkp.forms import FileSetForm, ComputerForm, ProcedureForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


### FileSets ###
@authentication_required
def new_fileset(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
        forms_dict['fsetform'] = FileSetForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_fileset.html', return_dict, context_instance=RequestContext(request))



@authentication_required
def create_fileset(request, computer_id, procedure_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['fsetform'] = FileSetForm(request.POST)
        
        if forms_dict['fsetform'].is_valid():
            fileset = FileSet()
            fileset.procedure_id = procedure_id
            fileset.path = forms_dict['fsetform'].cleaned_data['path']
            fileset.save()
            request.user.message_set.create(message="Local cadastrado com sucesso.")
            return HttpResponseRedirect(computer_path(request, computer_id))
        else:
            vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
            vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o local não foi cadastrado.")
            return render_to_response('bkp/new_fileset.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def delete_fileset(request, computer_id, procedure_id, fileset_id):
    if request.method == 'POST':
        fset = get_object_or_404(FileSet, pk=fileset_id)
        fset.delete()
        request.user.message_set.create(message="Local foi removido permanentemente.")
        return redirect_back_or_default(request, default=computer_path(request, computer_id))

