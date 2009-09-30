#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Storage, Procedure, GlobalConfig
from backup_corporativo.bkp.forms import StorageForm
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


@authentication_required
def new_storage(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    if request.method == 'GET':
        forms_dict['storform'] = StorageForm()
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/storage/new_storage.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def create_storage(request):
    vars_dict, forms_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        forms_dict['storform'] = StorageForm(request.POST)
        forms_list = forms_dict.values()
        if all([form.is_valid() for form in forms_list]):
            storage = forms_dict['storform'].save()
            location = utils.path("storage", sto_id, request)
            return HttpResponseRedirect(location)
        else:
            request.user.message_set.create(
                message="Existem erros e o storage não foi cadastrado.")
            return_dict = utils.merge_dicts(forms_dict, vars_dict, temp_dict)
            return render_to_response(
                'templates/bkp/storage/new_storage.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def view_storage(request, sto_id):
    vars_dict, forms_dict = global_vars(request)

    if request.method == 'GET':
        vars_dict['storage'] = get_object_or_404(Storage, pk=sto_id)
        vars_dict['procedures'] = Procedure.objects.filter(
            storage=vars_dict['storage'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/storage/view_storage.html',
            return_dict,
            context_instance=RequestContext(request))

@authentication_required
def edit_storage(request, sto_id):
    vars_dict, forms_dict = global_vars(request)
    vars_dict['storage'] = get_object_or_404(Storage, pk=sto_id)
    if request.method == 'GET':
        forms_dict['storform'] = StorageForm(
            instance=vars_dict['storage'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/storage/edit_storage.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_storage(request, sto_id):
    vars_dict, forms_dict = global_vars(request)
    vars_dict['storage'] = get_object_or_404(Storage, pk=sto_id)
    if request.method == 'POST':
        forms_dict['storform'] = StorageForm(
            request.POST,
            instance=vars_dict['storage'])
        if forms_dict['storform'].is_valid():
            forms_dict['storform'].save()
            request.user.message_set.create(
                message="Storage foi alterado com sucesso.")
            location = utils.path("storage", sto_id, request)
            return HttpResponseRedirect(location)
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            request.user.message_set.create(
                message="Existem erros e o storage não foi alterado.")
            return render_to_response(
                'templates/bkp/storage/edit_storage.html',
                return_dict,
                context_instance=RequestContext(request))   


@authentication_required
def delete_storage(request, sto_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['storage'] = get_object_or_404(Storage, pk=sto_id)
        request.user.message_set.create(
            message="Confirme a remoção do storage.")
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/storage/delete_storage.html',
            return_dict,
            context_instance=RequestContext(request))
    #TODO: separar em dois objetos de view
    elif request.method == 'POST':
        storage = get_object_or_404(Storage, pk=sto_id)
        storage.delete()
        request.user.message_set.create(
            message="Storage removido permanentemente.")
        #TODO: configurar default location
        return utils.redirect_back(request)


@authentication_required
def dump_storage_config(request, sto_id):
    """Generates and offers to download a storage config file."""
    storage = Storage.objects.get(id=sto_id)
    dump_list = storage.dump_storagedaemon_config()
    dump_file = ''.join(dump_list)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
    response.write(dump_file)
    return response


@authentication_required
def view_storage_config(request, sto_id):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['sto'] = Storage.objects.get(pk=sto_id)
        vars_dict['storage_config'] = \
            vars_dict['sto'].dump_storagedaemon_config()
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/storage/view_storage_config.html',
            return_dict,
            context_instance=RequestContext(request))