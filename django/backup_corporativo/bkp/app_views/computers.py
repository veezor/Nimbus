#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from environment import ENV

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Computer, GlobalConfig
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, FileSetForm, WizardAuxForm
from backup_corporativo.bkp.views import global_vars, authentication_required, DAYS_OF_THE_WEEK


@authentication_required
def new_computer(request):
    E = ENV(request)

    if request.method == 'GET':
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        if Computer.objects.count() > 14:
            E.msg = u"Erro ao adicionar computador: limite de computadores foi atingido."
            location = reverse('list_computers')
            return HttpResponseRedirect(location)
        E.compform = ComputerForm(instance=Computer())
        E.template = 'bkp/computer/new_computer.html'
        return E.render()


@authentication_required
def create_computer(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.compform = ComputerForm(request.POST, instance=Computer())
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            E.wizard = E.wizauxform.cleaned_data['wizard']
        # Apenas por segurança
        else:
            E.wizard = False
        if Computer.objects.count() > 14:
            E.msg = u"Erro ao adicionar computador: limite de computadores foi atingido."
            location = reverse('list_computers')
            return HttpResponseRedirect(location)
        if E.compform.is_valid():
            comp = E.compform.save()
            location = reverse('new_computer_backup', [comp.id])
            location += "?wizard=%s" % E.wizard
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/computer/new_computer.html'
            return E.render()


@authentication_required
def edit_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(instance=E.comp)
        E.template = 'bkp/computer/edit_computer.html',
        return E.render()


@authentication_required
def update_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(request.POST,instance=E.comp)
        if E.compform.is_valid():
            E.compform.save()
            E.msg = u"Computador foi alterado com sucesso."
            location = reverse('view_computer', args=[comp_id])
            return HttpResponseRedirect(location)
        else:
            E.msg = u"Erro ao alterar computador."
            E.template = 'bkp/computer/edit_computer.html'
            return E.render()


@authentication_required
def view_computer(request, comp_id):
    E = ENV(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        E.procs = E.comp.procedure_set.all()
        E.running_jobs = E.comp.running_jobs()
        E.last_jobs = E.comp.last_jobs()
        E.compstatus = E.comp.get_status()
        E.DAYS_OF_THE_WEEK = DAYS_OF_THE_WEEK
        E.template = 'bkp/computer/view_computer.html'
        return E.render()


@authentication_required
def delete_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        E.template = 'bkp/computer/delete_computer.html'
        return E.render()
    elif request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.delete()
        E.msg = u"Computador foi removido permanentemente."
        return HttpResponseRedirect(reverse("list_computers"))


@authentication_required
def test_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.run_test_job()
        E.msg = u"Uma requisiçao foi enviada ao computador."
        location = reverse("view_computer", args=[comp_id])
        return HttpResponseRedirect(location)


@authentication_required
def view_computer_config(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.comp = Computer.objects.get(pk=comp_id)
        E.comp_config = E.comp.dump_filedaemon_config()
        E.template = 'bkp/computer/view_computer_config.html'
        return E.render()


@authentication_required
def dump_computer_config(request, comp_id):
    if request.method == 'POST':
        computer = Computer.objects.get(pk=comp_id)
        dump_list = computer.dump_filedaemon_config()
        dump_file = ''.join(dump_list)
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=bacula-fd.conf'
        response.write(dump_file)
        return response
    
    
@authentication_required
def new_computer_backup(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.comp = get_object_or_404(Computer, pk=comp_id)            
        E.procform = ProcedureForm()
        E.fsetform = FileSetForm()    
        E.template = 'bkp/computer/new_computer_backup.html'
        return E.render()


@authentication_required
def create_computer_backup(request, comp_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            wiz = E.wizauxform.cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        E.comp = get_object_or_404(Computer, pk=comp_id)            
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
            location = reverse("new_procedure_schedule", args=[proc.id])
            location += "?wizard=%s" % wiz
            return HttpResponseRedirect(location)
        else:
            E.wizard = wiz
            E.template = 'bkp/computer/new_computer_backup.html'
            return E.render()