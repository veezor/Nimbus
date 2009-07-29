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
        return render_to_response('bkp/new/new_storage.html', return_dict, context_instance=RequestContext(request))


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
            return render_to_response('bkp/new/new_storage.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def view_storage(request, storage_id):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        # Load forms and vars
        #forms_dict['storform'] = StorageForm()
        vars_dict['storage'] = get_object_or_404(Storage, pk=storage_id)
        vars_dict['procedures'] = Procedure.objects.filter(storage = vars_dict['storage'])
        
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_storage.html', return_dict, context_instance=RequestContext(request))
        

@authentication_required
def edit_storage(request, storage_id):
    vars_dict, forms_dict, return_dict = global_vars(request)
    storage = get_object_or_404(Storage, pk=storage_id)
    vars_dict['storage'] = storage

    if request.method == 'GET': # Edit computer
        forms_dict['storform'] = StorageForm(instance=storage)
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_storage.html', return_dict, context_instance=RequestContext(request))


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
            return render_to_response('bkp/edit/edit_storage.html', return_dict, context_instance=RequestContext(request))   


@authentication_required
def delete_storage(request, storage_id):
    if request.method == 'GET':
        vars_dict, forms_dict, return_dict = global_vars(request)
        vars_dict['storage'] = get_object_or_404(Storage, pk=storage_id)
        request.user.message_set.create(message="Confirme a remoção do storage.")
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/delete/delete_storage.html', return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        storage = get_object_or_404(Storage, pk=storage_id)
        storage.delete()
        request.user.message_set.create(message="Storage removido permanentemente.")
        return redirect_back_or_default(request, default=root_path(request))

# TODO remove code from view, move it to models.py
def generate_storage_dump_file(storage, config):
    "generate config file"
    sto_dict = {'Name': storage.storage_name, 'SDPort': storage.storage_port,
                    'WorkingDirectory': '"/var/bacula/working"',
                    'Pid Directory': '"/var/run"',
                    'Maximum Concurrent Jobs': '20'}
    dir_dict = {'Name': config.bacula_name,
                    'Password': '"%s"' % config.storage_password}
    dev_dict = {'Name': "FileStorage", 'Media Type': 'File',
                    'Archive Device': '/var/backup', 'LabelMedia': 'yes', 
                    'Random Access': 'yes', 'AutomaticMount': 'yes',
                    'RemovableMedia': 'no', 'AlwaysOpen': 'no'}
    msg_dict = {'Name': "Standard", 'Director':'%s = all' % config.bacula_name}
    
    s = []

    s.append("Storage {\n")
    for k in sto_dict.keys():
        s.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':sto_dict[k]})
    s.append("}\n\n")

    s.append("Director {\n")
    for k in dir_dict.keys():
        s.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
    s.append("}\n\n")
    
    s.append("Device {\n")
    for k in dev_dict.keys():
        s.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dev_dict[k]})
    s.append("}\n\n")
    
    s.append("Messages {\n")
    for k in msg_dict.keys():
        s.append('''\t%(key)s = %(value)s\n''' % {'key':k,'value':msg_dict[k]})
    s.append("}\n\n")
    
    return ''.join(s)


@authentication_required
def storage_config_dump(request, storage_id):
    """Generates and offers to download a storage config file."""
    storage = Storage.objects.get(id=storage_id)
    config = GlobalConfig.objects.get(pk=1)
    dump_file = generate_storage_dump_file(storage, config)
    
	# Return file for download
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
    response.write(dump_file)
    return response

