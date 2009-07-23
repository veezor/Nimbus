#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import Storage, GlobalConfig
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
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_storage.html', return_dict, context_instance=RequestContext(request))


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
    from time import strftime
    from backup_corporativo.bkp.crypt_utils import encrypt, decrypt
    from backup_corporativo.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME
    try:
        from backup_corporativo.settings import BACULA_DB_NAME
    except:
        raise('Could not import BACULA_DB_NAME from settings.py')
    
    storage = Storage.objects.get(id=storage_id)
    config = GlobalConfig.objects.all()[0]
    dump_file = generate_storage_dump_file(storage, config)
    
	# Return file for download
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
    response.write(dump_file)
    
    return response

