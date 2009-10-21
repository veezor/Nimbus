#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, GlobalConfig
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, FileSetForm, WizardAuxForm
# TODO move to utils
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


# TODO: enviar informação de wizard pro POST através de formuário auxiliar
@authentication_required
def new_computer(request):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'GET':
        if 'wizard' in request.GET:
            vars_dict['wizard'] = request.GET['wizard']
        else:
            vars_dict['wizard'] = False
        forms_dict['compform'] = ComputerForm(instance=Computer())
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/new_computer.html',
            return_dict, context_instance=RequestContext(request))


@authentication_required
def create_computer(request):
    if request.method == 'POST':
        vars_dict, forms_dict = global_vars(request)
        aux_dict = {}
        c = Computer()
        forms_dict['compform'] = ComputerForm(request.POST, instance=c)
        aux_dict['wizauxform'] = WizardAuxForm(request.POST)
        if aux_dict['wizauxform'].is_valid():
            wiz = aux_dict['wizauxform'].cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        if forms_dict['compform'].is_valid():
            comp = forms_dict['compform'].save()
            location = utils.new_computer_backup(comp.id, request, wizard=wiz)
            return HttpResponseRedirect(location)
        else:
            vars_dict['wizard'] = wiz
            return_dict = utils.merge_dicts(forms_dict, vars_dict, aux_dict)
            return render_to_response(
                'bkp/computer/new_computer.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def edit_computer(request, comp_id):
    vars_dict, forms_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=comp_id)
    if request.method == 'GET':
        forms_dict['compform'] = ComputerForm(instance=vars_dict['comp'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/edit_computer.html',
            return_dict, context_instance=RequestContext(request))
# Tratamento de erros para outros métodos de requisição.
#    elif request.method == 'POST':
#        raise Exception(
#            """Erro de programação.
#            Método de Requisição "%s" é inesperado.
#            Recebido por app_views/computers.py.""" % request.method)
#    else:
#        raise Exception(
#            """Erro de programação.
#            Método de Requisição "%s" é inesperado.
#            Recebido por app_views/computers.py.""" % request.method)


@authentication_required
def update_computer(request, comp_id):
    vars_dict, forms_dict = global_vars(request)
    comp = get_object_or_404(Computer, pk=comp_id)
    vars_dict['comp'] = comp
    if request.method == 'POST':
        forms_dict['compform'] = ComputerForm(request.POST,instance=comp)
        if forms_dict['compform'].is_valid():
            forms_dict['compform'].save()
            request.user.message_set.create(
                message="Computador foi alterado com sucesso.")
            return HttpResponseRedirect(
                utils.path("computer", comp_id, request))
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            request.user.message_set.create(
                message="Existem erros e o computador não foi alterado.")
            return render_to_response(
                'bkp/computer/edit_computer.html',
                return_dict, context_instance=RequestContext(request))   


@authentication_required
def view_computer(request, comp_id):
    vars_dict, forms_dict = global_vars(request)
    utils.store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer,pk=comp_id)
        vars_dict['procs'] = vars_dict['comp'].procedure_set.all()
        vars_dict['running_jobs'] = vars_dict['comp'].running_jobs()
        vars_dict['last_jobs'] = vars_dict['comp'].last_jobs()
        from backup_corporativo.bkp.bacula import Bacula
        vars_dict['compstatus'] = vars_dict['comp'].get_status()
        # Load forms and vars
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/view_computer.html',
            return_dict, context_instance=RequestContext(request))    


#TODO: dividir em dois objetos de view diferentes.
@authentication_required
def delete_computer(request, comp_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer,pk=comp_id)
        request.user.message_set.create(
            message="Confirme a remoção do computador.")
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/delete_computer.html',
            return_dict, context_instance=RequestContext(request))    
    elif request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.delete()
        request.user.message_set.create(
            message="Computador removido permanentemente.")            
        return HttpResponseRedirect(utils.root_path(request))


@authentication_required
def test_computer(request, comp_id):
    if request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.run_test_job()
        request.user.message_set.create(
            message="Uma requisição foi enviada para o computador.")
        return HttpResponseRedirect(
            utils.path("computer", comp_id, request))


@authentication_required
def view_computer_config(request, comp_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['comp'] = Computer.objects.get(pk=comp_id)
        vars_dict['comp_config'] = vars_dict['comp'].dump_filedaemon_config()
        # Load forms and vars
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/view_computer_config.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def dump_computer_config(request, comp_id):
    if request.method == 'POST':
        computer = Computer.objects.get(pk=comp_id)
        dump_list = computer.dump_filedaemon_config()
        dump_file = ''.join(dump_list)
        # Return file for download
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=bacula-fd.conf'
        response.write(dump_file)
        return response
    
    
@authentication_required
def new_computer_backup(request, comp_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        temp_dict = {}
        if 'wizard' in request.GET:
            vars_dict['wizard'] = request.GET['wizard']
        else:
            vars_dict['wizard'] = False
        vars_dict['comp'] = get_object_or_404(Computer, pk=comp_id)            
        forms_dict['procform'] = ProcedureForm()
        forms_dict['fsetform'] = FileSetForm()    
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/new_computer_backup.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def create_computer_backup(request, comp_id):
    if request.method == 'POST':
        vars_dict, forms_dict = global_vars(request)
        aux_dict = {}
        aux_dict['wizauxform'] = WizardAuxForm(request.POST)
        if aux_dict['wizauxform'].is_valid():
            wiz = aux_dict['wizauxform'].cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        vars_dict['comp'] = get_object_or_404(Computer, pk=comp_id)            
        forms_dict['procform'] = ProcedureForm(request.POST)
        forms_dict['fsetform'] = FileSetForm(request.POST)
        forms_list = forms_dict.values()
        if all([form.is_valid() for form in forms_list]):
            proc = forms_dict['procform'].save(commit=False)
            fset = forms_dict['fsetform'].save(commit=False)
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
            vars_dict['wizard'] = wiz
            return_dict = utils.merge_dicts(forms_dict, vars_dict, aux_dict)
            return render_to_response(
                'bkp/computer/new_computer_backup.html',
                return_dict,
                context_instance=RequestContext(request))