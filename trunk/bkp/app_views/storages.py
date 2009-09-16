#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Storage, Procedure, GlobalConfig
from backup_corporativo.bkp.forms import StorageForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
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
        # Load forms and vars
        forms_dict['storform'] = StorageForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/new/new_storage.html', return_dict,
            context_instance=RequestContext(request))


@authentication_required
def create_storage(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    temp_dict = {}

    if request.method == 'POST':
        forms_dict['storform'] = StorageForm(request.POST)
        forms_list = forms_dict.values()
        if all([form.is_valid() for form in forms_list]):
            storage = forms_dict['storform'].save()
            return HttpResponseRedirect(storage_path(request, storage.id))
        else:
            # Load forms and vars
            request.user.message_set.create(message="Existem erros e o storage não foi cadastrado.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict, temp_dict)
            return render_to_response(
                'bkp/new/new_storage.html',
                return_dict, context_instance=RequestContext(request))


@authentication_required
def view_storage(request, storage_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        # Load forms and vars
        #forms_dict['storform'] = StorageForm()
        vars_dict['storage'] = get_object_or_404(Storage, pk=storage_id)
        vars_dict['procedures'] = Procedure.objects.filter(storage = vars_dict['storage'])
        
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/view/view_storage.html',
            return_dict, context_instance=RequestContext(request))
        

@authentication_required
def edit_storage(request, storage_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    storage = get_object_or_404(Storage, pk=storage_id)
    vars_dict['storage'] = storage

    if request.method == 'GET': # Edit computer
        forms_dict['storform'] = StorageForm(instance=storage)
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/edit/edit_storage.html',
            return_dict, context_instance=RequestContext(request))


@authentication_required
def update_storage(request, storage_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    storage = get_object_or_404(Storage, pk=storage_id)
    vars_dict['storage'] = storage

    if request.method == 'POST':
        forms_dict['storform'] = StorageForm(request.POST, instance=storage)
        
        if forms_dict['storform'].is_valid():
            forms_dict['storform'].save()
            request.user.message_set.create(message="Storage foi alterado com sucesso.")
            return HttpResponseRedirect(storage_path(request, storage_id))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e o storage não foi alterado.")
            return render_to_response(
                'bkp/edit/edit_storage.html',
                return_dict, context_instance=RequestContext(request))   


@authentication_required
def delete_storage(request, storage_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['storage'] = get_object_or_404(Storage, pk=storage_id)
        request.user.message_set.create(message="Confirme a remoção do storage.")
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/delete/delete_storage.html',
            return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        storage = get_object_or_404(Storage, pk=storage_id)
        storage.delete()
        request.user.message_set.create(message="Storage removido permanentemente.")
        return redirect_back_or_default(request, default=root_path(request))


@authentication_required
def dump_storage_config(request, storage_id):
    """Generates and offers to download a storage config file."""
    storage = Storage.objects.get(id=storage_id)
    dump_list = storage.dump_storagedaemon_config()
    dump_file = ''.join(dump_list)
    
    # Return file for download
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
    response.write(dump_file)
    return response


@authentication_required
def view_storage_config(request, storage_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['sto'] = Storage.objects.get(pk=storage_id)
        vars_dict['storage_config'] = vars_dict['sto'].dump_storagedaemon_config()
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response(
            'bkp/view/view_storage_config.html',
            return_dict, context_instance=RequestContext(request))
