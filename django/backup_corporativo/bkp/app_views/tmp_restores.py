#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from environment import ENV

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.views import global_vars, authentication_required
from backup_corporativo.bkp.models import Computer, Procedure
from backup_corporativo.bkp.forms import RestoreForm, HiddenRestoreForm, RestoreCompForm, RestoreProcForm
from backup_corporativo.bkp.bacula import Bacula


def new_restore(request):
    E = ENV(request)

    if request.method == 'GET':
        E.restore_step = 0
        E.restorecomp_form = RestoreCompForm()
        E.template = 'bkp/wizard/restore/restore_wizard.html'
        return E.render()


def create_restore(request):
        E = ENV(request)

        if request.method == 'POST':
            E.restore_step = 0
            E.restorecomp_form = RestoreCompForm(request.POST)
            if E.restorecomp_form.is_valid():
                comp_id = E.restorecomp_form.cleaned_data['target_client']
                location = reverse('new_computer_restore', args=[comp_id])
                return HttpResponseRedirect(location)
            else:
                E.template = 'bkp/wizard/restore/restore_wizard.html'
                return E.render()


def new_computer_restore(request, comp_id):
    E = ENV(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.restore_step = 1
        E.restoreproc_form = RestoreProcForm()
        E.restoreproc_form.load_choices(comp_id)
        E.template = 'bkp/wizard/restore/restore_wizard.html'
        return E.render()


def create_computer_restore(request, comp_id):
    E = ENV(request)

    if request.method == 'POST':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.restore_step = 1
        E.restoreproc_form = RestoreProcForm(request.POST)
        E.restoreproc_form.load_choices(comp_id)
        if E.restoreproc_form.is_valid():
            proc_id = E.restoreproc_form.cleaned_data['target_procedure']
            location = reverse('new_procedure_restore', args=[comp_id, proc_id])
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/wizard/restore/restore_wizard.html'
            return E.render()



def new_procedure_restore(request, comp_id, proc_id):
    E = ENV(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.restore_step = 2
        E.restore_jobs = E.proc.restore_jobs()
        E.template = 'bkp/wizard/restore/restore_wizard.html'
        return E.render()


#def create_procedure_restore

def new_job_restore(request, comp_id, proc_id, job_id):
    E = ENV(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.proc = get_object_or_404(Procedure, pk=proc_id)    
        E.job_id = job_id
        E.restore_step = 3
        E.src_client = request.GET['src']
        E.target_dt = request.GET['dt']
        E.fileset_name = request.GET['fset']
        E.file_count, E.file_tree = E.proc.get_file_tree(job_id)
        E.restore_form = RestoreForm()
        E.template = 'bkp/wizard/restore/restore_wizard.html'
        return E.render()


def create_job_restore(request, comp_id, proc_id, job_id):
    E = ENV(request)

    if request.method == 'POST':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.proc = get_object_or_404(Procedure, pk=proc_id)
        E.job_id = job_id
        E.restore_step = 3
        E.restore_form = RestoreForm(request.POST)
        E.hidden_restore_form = HiddenRestoreForm(request.POST)
        if E.hidden_restore_form.is_valid():
            E.src_client = E.hidden_restore_form.cleaned_data['client_source']
            E.target_dt = E.hidden_restore_form.cleaned_data['target_dt']
            E.fileset_name = E.hidden_restore_form.cleaned_data['fileset_name']
        else:
            emsg = 'Erro de programacao: hidden_restore_form invalido'
            raise Exception(emsg)
        if E.restore_form.is_valid():
            client_from_restore = E.comp.computer_bacula_name()
            client_to_restore = E.restore_form.cleaned_data['client_restore']
            date_to_restore = E.target_dt
            directory_to_restore = E.restore_form.cleaned_data['restore_path']
            fileset_name = E.fileset_name
            raw_file_list = request.POST.getlist('dir')
            # Generating list of list.
            file_list = []
            for f in raw_file_list:
                f = f.split('/')
                file_list.append(['%s/' % i for i in f[:-1]] + [f[-1]])
            bacula = Bacula()
            bacula.tmp_restore(client_from_restore, client_to_restore, date_to_restore, directory_to_restore, fileset_name, file_list)
            location = reverse("view_computer", [E.comp.id])
            return HttpResponseRedirect(location)
        else:
            E.file_count, E.file_tree = E.proc.get_file_tree(job_id)
            E.template = 'bkp/wizard/restore/restore_wizard.html'
            return E.render()
