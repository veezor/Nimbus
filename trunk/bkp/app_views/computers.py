#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Computer, GlobalConfig
from backup_corporativo.bkp.forms import ComputerForm
# TODO move to utils
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


@authentication_required
def edit_computer(request, comp_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['comp'] = get_object_or_404(Computer, pk=comp_id)
    if request.method == 'GET':
        forms_dict['compform'] = ComputerForm(instance=vars_dict['comp'])
        return_dict = utils.merge_dicts(
            return_dict,
            forms_dict,
            vars_dict)
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
    vars_dict, forms_dict, return_dict = global_vars(request)
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
            return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(
                message="Existem erros e o computador não foi alterado.")
            return render_to_response(
                'bkp/computer/edit_computer.html',
                return_dict, context_instance=RequestContext(request))   

@authentication_required
def view_computer(request, comp_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    utils.store_location(request)
    if request.method == 'GET':
        vars_dict['comp'] = get_object_or_404(Computer,pk=comp_id)
        vars_dict['procs'] = vars_dict['comp'].procedure_set.all()
        vars_dict['running_jobs'] = vars_dict['comp'].running_jobs()
        vars_dict['last_jobs'] = vars_dict['comp'].last_jobs()
        from backup_corporativo.bkp.bacula import Bacula
        vars_dict['compstatus'] = vars_dict['comp'].get_status()
        # Load forms and vars
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/view_computer.html',
            return_dict, context_instance=RequestContext(request))    


#TODO: dividir em dois objetos de view diferentes.
@authentication_required
def delete_computer(request, comp_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = get_object_or_404(Computer,pk=comp_id)
        request.user.message_set.create(
            message="Confirme a remoção do computador.")
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
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
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['comp'] = Computer.objects.get(pk=comp_id)
        vars_dict['comp_config'] = vars_dict['comp'].dump_filedaemon_config()
        # Load forms and vars
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/computer/view_computer_config.html',
            return_dict, context_instance=RequestContext(request))


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