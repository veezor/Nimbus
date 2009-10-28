#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Storage
from backup_corporativo.bkp.forms import StrongBoxForm
from backup_corporativo.bkp.views import global_vars, authentication_required

from keymanager import KeyManager

@authentication_required
def main_management(request):
    vars_dict, forms_dict = global_vars(request)

    if request.method == 'GET':
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/management/main_management.html',
            return_dict,
            context_instance=RequestContext(request)
        )


@authentication_required
def list_computers(request):
    vars_dict, forms_dict = global_vars(request)

    if request.method == 'GET':
        # Reaproveitar lista de computadores declarada em global_vars()
        vars_dict['comp_list'] = vars_dict['comps']
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/management/list_computers.html',
            return_dict, context_instance=RequestContext(request)
        )


@authentication_required
def list_storages(request):
    vars_dict, forms_dict = global_vars(request)

    if request.method == 'GET':
        vars_dict['sto_list'] = Storage.objects.all()
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/management/list_storages.html',
            return_dict,
            context_instance=RequestContext(request)
        )


@authentication_required
def manage_strongbox(request):
    vars_dict, forms_dict = global_vars(request)
    
    km = KeyManager()
    if not km.has_drive():
        return HttpResponseRedirect(utils.new_strongbox_path(request))

    if request.method == 'GET':
        vars_dict['drive_mounted'] = km.drive_mounted()
        if not vars_dict['drive_mounted']:
            forms_dict['mountstrongbox_form'] = MountStrongBoxForm()
        return_dict = utils.merge_dicts(vars_dict, forms_dict)
        return render_to_response(
            'bkp/management/manage_strongbox.html',
            return_dict,
            context_instance=RequestContext(request)
        )


@authentication_required
def new_strongbox(request):
    vars_dict, forms_dict = global_vars(request)

    km = KeyManager()
    if km.has_drive():
        #TODO: adicionar mensagem: drive já existe.
        return HttpResponseRedirect(utils.manage_strongbox(request))

    if request.method == 'GET':
        forms_dict['newstrongbox_form'] = NewStrongBoxForm(request.POST)
        return_dict = utils.merge_dicts(vars_dict, forms_dict)
        return render_to_response(
            'bkp/management/new_strongbox.html',
            return_dict,
            context_instance=RequestContext(request)
        )


@authentication_required
def create_strongbox(request):
    vars_dict, forms_dict = global_vars(request)

    km = KeyManager()
    if km.has_drive():
        #TODO: adicionar mensagem: drive já existe.
        return HttpResponseRedirect(utils.manage_strongbox(request))

    if request.method == 'POST':
        forms_dict['newstrongbox_form'] = NewStrongBoxForm(request.POST)
        if forms_dict['newstrongbox_form'].is_valid():
            return HttpResponseRedirect(utils.manage_strongbox(request))
        else:
            return_dict = utils.merge_dicts(vars_dict, forms_dict)
            return render_to_response(
                'bkp/management/new_strongbox.html',
                return_dict,
                context_instance=RequestContext(request)
            )


@authentication_required
def umount_strongbox(request):
    vars_dict, forms_dict = global_vars(request)
    
    km = KeyManager()
    if not km.drive_mounted():
        #TODO: adicionar mensagem: cofre já está travado.
        return HttpResponseRedirect(utils.manage_strongbox_path(request))

    if request.method == 'GET':
        return_dict = utils.merge_dicts(vars_dict, forms_dict)
        return render_to_response(
            'bkp/management/umount_strongbox.html',
            return_dict,
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        # Está faltando a opção de forçar desmontagem.
        km.umount_drive()
        return HttpResponseRedirect(utils.manage_strongbox_path(request))

@authentication_required
def changepwd_strongbox(request):
    vars_dict, forms_dict = global_vars(request)
    
    km = KeyManager()
    if km.drive_mounted():
        #TODO: adicionar mensagem: é necessário fechar cofre antes de trocar senha.
        return HttpResponseRedirect(utils.umount_strongbox_path(request))

    if request.method == 'GET':
        forms_dict['changepwdsb_form'] = ChangePwdStrongBoxForm()
        return_dict = utils.merge_dicts(vars_dict, forms_dict)
        return render_to_response(
            'bkp/management/changepass_strongbox.html',
            return_dict,
            context_instance=RequestContext(request)
        )
    elif request.method == 'POST':
        forms_dict['changepwdsb_form'] = ChangePwdStrongBoxForm(request.POST)
        if forms_dict['changepwdsb_form'].is_valid():
            return HttpResponseRedirect(utils.manage_strongbox_path(request))
        else:
            return_dict = utils.merge_dicts(vars_dict, forms_dict)
            return render_to_response(
                'bkp/management/changepass_strongbox.html',
                return_dict,
                context_instance=RequestContext(request)
            )


