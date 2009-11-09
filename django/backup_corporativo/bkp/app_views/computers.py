#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, GlobalConfig
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, FileSetForm, WizardAuxForm
from backup_corporativo.bkp.views import global_vars, authentication_required


# TODO: enviar informação de wizard pro POST através de formuário auxiliar
@authentication_required
def new_computer(request):
    E.update(request)

    if request.method == 'GET':
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.compform = ComputerForm(instance=Computer())
        E.template = 'bkp/computer/new_computer.html'
        return E.render()


@authentication_required
def create_computer(request):
    E.update(request)
    
    if request.method == 'POST':
        E.compform = ComputerForm(request.POST, instance=Computer())
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            wiz = E.wizauxform.cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        if E.compform.is_valid():
            comp = E.compform.save()
            location = utils.new_computer_backup(comp.id, request, wizard=wiz)
            return HttpResponseRedirect(location)
        else:
            E.wizard = wiz
            E.template = 'bkp/computer/new_computer.html'
            return E.render()


@authentication_required
def edit_computer(request, comp_id):
    E.update(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(instance=E.comp)
        E.template = 'bkp/computer/edit_computer.html',
        return E.render()


@authentication_required
def update_computer(request, comp_id):
    E.update(request)
    
    if request.method == 'POST':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(request.POST,instance=E.comp)
        if E.compform.is_valid():
            E.compform.save()
            E,msg(_("Computador foi alterado com sucesso."))
            location = utils.path("computer", comp_id, request)
            return HttpResponseRedirect(location)
        else:
            E.msg = _("Existem erros e o computador não foi alterado.")
            E.template = 'bkp/computer/edit_computer.html'
            return E.render()


@authentication_required
def view_computer(request, comp_id):
    E.update(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        E.procs = E.comp.procedure_set.all()
        E.running_jobs = E.comp.running_jobs()
        E.last_jobs = E.comp.last_jobs()
        E.compstatus = E.comp.get_status()
        E.template = 'bkp/computer/view_computer.html'
        return E.render()


@authentication_required
def delete_computer(request, comp_id):
    E.update(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        E.msg(_("Confirme a remoção do computador."))
        E.template = 'bkp/computer/delete_computer.html'
        return E.render()
    elif request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.delete()
        E.msg = _("Computador removido permanentemente.")
        return HttpResponseRedirect(utils.root_path(request))


@authentication_required
def test_computer(request, comp_id):
    E.update(request)
    
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.run_test_job()
        E.msg = _("Uma requisição foi enviada para o computador.")
        location = utils.path("computer", comp_id, request)
        return HttpResponseRedirect(location)


@authentication_required
def view_computer_config(request, comp_id):
    E.update(request)
    
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
    E.update(request)
    
    if request.method == 'GET':
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.comp = get_object_or_404(Computer, pk=comp_id)            
        E.procform = ProcedureForm()
        E.fsetform = FileSetForm()    
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        E.template = 'bkp/computer/new_computer_backup.html'
        return E.render()


@authentication_required
def create_computer_backup(request, comp_id):
    E.update(request)
    
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
            location = utils.new_procedure_schedule(
                proc.id,
                request,
                wizard=wiz)
            return HttpResponseRedirect(location)
        else:
            E.wizard = wiz
            E.template = 'bkp/computer/new_computer_backup.html'
            E.render()