#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.forms import RestoreForm
from backup_corporativo.bkp.forms import HiddenRestoreForm
from backup_corporativo.bkp.forms import RestoreCompForm, RestoreProcForm
from backup_corporativo.bkp.bacula import Bacula
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

# NOTA:
# Utilizar argumento padrão na assinatura da view não 
# é um comportamento padrão do django, e faz com que o
# retorno da função get_object_or_404 confunda o modo
# de debug do django. Quando ele retorna 404, o servidor
# perde todas as rotas e mostra apenas uma página de 404
# mesmo no modo debug ativado
# Para resolver isso, será necessário exclusivamente aqui, 
# tratar os erros Model.DoesNotExist com blocos "Try e Except"
# TODO: trocar get_object_or_404 por Try classe.objects.get e Except classe.DoesNotExist
@authentication_required
def new_restore(request, computer_id=None, procedure_id=None, job_id=None):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}
    if computer_id is not None:
        vars_dict['comp'] = get_object_or_404(Computer, pk=computer_id)
    if procedure_id is not None:
        vars_dict['proc'] = get_object_or_404(Procedure, pk=procedure_id)
    if job_id is not None:
        vars_dict['job_id'] = job_id

    if request.method == 'GET':
        vars_dict['restore_step'] = __restore_step(computer_id, procedure_id, job_id)
        
        if vars_dict['restore_step'] == 0:
            vars_dict['restorecomp_form'] = RestoreCompForm()
        if vars_dict['restore_step'] == 1:
            forms_dict['restoreproc_form'] = RestoreProcForm()
            forms_dict['restoreproc_form'].load_choices(computer_id)
        if vars_dict['restore_step'] == 2:
            vars_dict['restore_jobs'] = vars_dict['proc'].restore_jobs()
        if vars_dict['restore_step'] == 3:
            __check_request(request)
            vars_dict['src_client'] = request.GET['src'] #TODO: trocar esse parametro por comp.computer_name
            vars_dict['target_dt'] = request.GET['dt']
            vars_dict['fileset_name'] = request.GET['fset']
            vars_dict['file_count'],vars_dict['file_tree'] = vars_dict['proc'].get_file_tree(job_id)            
            forms_dict['restore_form'] = RestoreForm()
            
            
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/tmp/new_restore.html', return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        vars_dict['restore_step'] = __restore_step(computer_id, procedure_id, job_id)
        
        # computer_id is None and procedure_id is None and job_id is None
        if vars_dict['restore_step'] == 0:
            forms_dict['restorecomp_form'] = RestoreCompForm(request.POST)
            if forms_dict['restorecomp_form'].is_valid():
                comp_id = forms_dict['restorecomp_form'].cleaned_data['target_client']
                return HttpResponseRedirect(restore_computer_path(request, comp_id))
            else:
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response('bkp/tmp/new_restore.html', return_dict, context_instance=RequestContext(request))
        # computer_id is not None and procedure_id is None and job_id is None
        elif vars_dict['restore_step'] == 1:
            forms_dict['restoreproc_form'] = RestoreProcForm(request.POST)
            forms_dict['restoreproc_form'].load_choices(computer_id)
            if forms_dict['restoreproc_form'].is_valid():
                proc_id = forms_dict['restoreproc_form'].cleaned_data['target_procedure']
                return HttpResponseRedirect(restore_procedure_path(request, computer_id, proc_id))
            else:
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
                return render_to_response('bkp/tmp/new_restore.html', return_dict, context_instance=RequestContext(request))
        elif vars_dict['restore_step'] == 3:
            forms_dict['restore_form'] = RestoreForm(request.POST)
            temp_dict['hidden_restore_form'] = HiddenRestoreForm(request.POST)
        
            if temp_dict['hidden_restore_form'].is_valid():
                vars_dict['src_client'] = temp_dict['hidden_restore_form'].cleaned_data['client_source']
                vars_dict['target_dt'] = temp_dict['hidden_restore_form'].cleaned_data['target_dt']
                vars_dict['fileset_name'] = temp_dict['hidden_restore_form'].cleaned_data['fileset_name']

                if forms_dict['restore_form'].is_valid():
                    client_from_restore = vars_dict['comp'].computer_name
                    client_to_restore = forms_dict['restore_form'].cleaned_data['client_restore']
                    date_to_restore = vars_dict['target_dt']
                    directory_to_restore = forms_dict['restore_form'].cleaned_data['restore_path']
                    fileset_name = vars_dict['fileset_name']
                    file_list = request.POST.getlist('file')
                    Bacula.tmp_restore(client_from_restore, client_to_restore, date_to_restore, directory_to_restore, fileset_name, file_list)
                    return HttpResponseRedirect(computer_path(request, computer_id))
#                    return HttpResponse(request.POST.getlist('file'))
                else:
                    vars_dict['file_count'],vars_dict['file_tree'] = vars_dict['proc'].get_file_tree(job_id)        
                    return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
                    return render_to_response('bkp/tmp/new_restore.html', return_dict, context_instance=RequestContext(request))

                

def __restore_step(computer_id=None ,procedure_id=None, job_id=None):
    if all([arg is None for arg in [computer_id,procedure_id,job_id]]):
        return 0
    elif all([arg is None for arg in [procedure_id,job_id]]):
        return 1
    elif all([arg is None for arg in [job_id]]):
        return 2
    elif all([arg is not None for arg in [computer_id,procedure_id,job_id]]):
        return 3
    return -1 # Função nunca deverá chegar aqui.
        
def __check_request(request):
    if not 'fset' in request.GET:
        raise Exception('JobID parameter is missing.')
    if not 'dt' in request.GET:
        raise Exception('Date parameter is missing.')
    if not 'src' in request.GET:
        raise Exception('ClientName parameter is missing.')    