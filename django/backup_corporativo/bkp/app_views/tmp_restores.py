#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from environment import ENV

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.views import global_vars, authentication_required
from backup_corporativo.bkp.models import Computer, Procedure
from backup_corporativo.bkp.forms import RestoreForm, HiddenRestoreForm, RestoreCompForm, RestoreProcForm
from backup_corporativo.bkp.bacula import Bacula


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
def new_restore(request, comp_id=None, proc_id=None, job_id=None):
    E = ENV(request)
    
    if comp_id is not None:
        E.comp = get_object_or_404(Computer, pk=comp_id)
    if proc_id is not None:
        E.proc = get_object_or_404(Procedure, pk=proc_id)
    if job_id is not None:
        E.job_id = job_id

    if request.method == 'GET':
        E.restore_step = __restore_step(comp_id, proc_id, job_id)
        if E.restore_step == 0:
            E.restorecomp_form = RestoreCompForm()
        if E.restore_step == 1:
            E.restoreproc_form = RestoreProcForm()
            E.restoreproc_form.load_choices(comp_id)
        if E.restore_step == 2:
            E.restore_jobs = E.proc.restore_jobs()
        if E.restore_step == 3:
            __check_request(request)
            #TODO: trocar esse parametro por comp.computer_name
            E.src_client = request.GET['src']
            E.target_dt = request.GET['dt']
            E.fileset_name = request.GET['fset']
            E.file_count, E.file_tree = E.proc.get_file_tree(job_id)            
            E.restore_form = RestoreForm()
        E.template = 'bkp/wizard/restore/restore_wizard.html'
        return E.render()
    elif request.method == 'POST':
        E.restore_step = __restore_step(comp_id, proc_id, job_id)
        if E.restore_step == 0:
            E.restorecomp_form = RestoreCompForm(request.POST)
            if E.restorecomp_form.is_valid():
                comp_id = E.restorecomp_form.cleaned_data['target_client']
                location = utils.restore_computer_path(request, comp_id)
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/restore/restore_rizard.html'
                return E.render()
        elif E.restore_step == 1:
            E.restoreproc_form = RestoreProcForm(request.POST)
            E.restoreproc_form.load_choices(comp_id)
            if E.restoreproc_form.is_valid():
                proc_id = E.restoreproc_form.cleaned_data['target_procedure']
                location = utils.restore_procedure_path(request, comp_id, proc_id)
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/restore/restore_wizard.html'
                return E.render()
        elif E.restore_step == 3:
            E.restore_form = RestoreForm(request.POST)
            E.hidden_restore_form = HiddenRestoreForm(request.POST)
            if E.hidden_restore_form.is_valid():
                E.src_client = E.hidden_restore_form.cleaned_data['client_source']
                E.target_dt = E.hidden_restore_form.cleaned_data['target_dt']
                E.fileset_name = E.hidden_restore_form.cleaned_data['fileset_name']
                
                if E.restore_form.is_valid():
                    client_from_restore = E.comp.computer_name
                    client_to_restore = E.restore_form.cleaned_data['client_restore']
                    date_to_restore = E.target_dt
                    directory_to_restore = E.restore_form.cleaned_data['restore_path']
                    fileset_name = E.fileset_name
                    raw_file_list = request.POST.getlist('file')
                    # Generating list of list.
                    file_list = []
                    for f in raw_file_list:
                        f = f.split('/')
                        file_list.append(['%s/' % i for i in f[:-1]] + [f[-1]])
                    Bacula.tmp_restore(
                        client_from_restore,
                        client_to_restore,
                        date_to_restore,
                        directory_to_restore,
                        fileset_name,
                        file_list)
                    location = utils.computer_path(request, comp_id)
                    return HttpResponseRedirect(location)
                else:
                    E.file_count, E.file_tree = E.proc.get_file_tree(job_id)        
                    E.template = 'bkp/wizard/restore/restore_wizard.html'
                    return E.render()


def __restore_step(comp_id=None ,proc_id=None, job_id=None):
    if all([arg is None for arg in [comp_id,proc_id,job_id]]):
        return 0
    elif all([arg is None for arg in [proc_id,job_id]]):
        return 1
    elif all([arg is None for arg in [job_id]]):
        return 2
    elif all([arg is not None for arg in [comp_id,proc_id,job_id]]):
        return 3
    return -1 # Função nunca deverá chegar aqui.
        
def __check_request(request):
    if not 'fset' in request.GET:
        emsg = u'Erro de programação: parâmetro "JobID" está faltando.'
        raise Exception(emsg)
    if not 'dt' in request.GET:
        emsg = u'Erro de programação: parâmetro "Date" está faltando.'
        raise Exception(emsg)
    if not 'src' in request.GET:
        emsg = u'Erro de programação: parâmetro "ClientName" está faltando.'
        raise Exception(emsg)    