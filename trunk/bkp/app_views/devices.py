#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import ExternalDevice
from backup_corporativo.bkp.forms import ExternalDeviceForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Device ###
@authentication_required
def new_device(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        vars_dict['dev_dict'] = {}
        import os
        import re
        dict = {}
        label_re = '''LABEL="(?P<label>.*?)"'''
        uuid_re = '''UUID="(?P<uuid>.*?)"'''
        cmd = 'blkid'
        output = os.popen(cmd).read()
        lines = output.split('\n')
 
        for line in lines:
            label = uuid = None
            label_se = re.search(label_re, line)
            uuid_se = re.search(uuid_re, line)
 
            if label_se:
                label = label_se.group('label')
            if uuid_se:
                uuid = uuid_se.group('uuid')
            if label and uuid:
                vars_dict['dev_dict'][label] = uuid

        vars_dict['stub_dict'] = {}
        vars_dict['stub_dict']['ROXO'] = '5Y3E6323'
        vars_dict['stub_dict']['luke'] = '1YAE635AB'
        vars_dict['stub_dict']['preto'] = '943255CB'
            
        forms_dict['devform'] = ExternalDeviceForm()
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_device.html', return_dict, context_instance=RequestContext(request))


@authentication_required
def create_device(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['devform'] = ExternalDeviceForm(request.POST)
        
        if forms_dict['devform'].is_valid():
            forms_dict['devform'].save()
            request.user.message_set.create(message="Device adicionado com sucesso.")            
            return HttpResponseRedirect(root_path(request))
        else:
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/new_device.html', return_dict, context_instance=RequestContext(request))

