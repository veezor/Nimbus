#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.network_utils import NetworkInfo
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import GlobalConfig, NetworkInterface
from backup_corporativo.bkp.forms import NetworkInterfaceEditForm
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

@authentication_required
def edit_networkinterface(request):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'GET':
        vars_dict['iface'] = NetworkInterface.networkconfig()
        forms_dict['netform'] = NetworkInterfaceEditForm(
            instance=vars_dict['iface'])
        # Load forms and vars 
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'templates/bkp/system/config_networkinterface_module.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_networkinterface(request):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'POST':
        vars_dict['iface'] = NetworkInterface.networkconfig()
        forms_dict['netform'] = NetworkInterfaceEditForm(
            request.POST,
            instance=vars_dict['iface'])
        if forms_dict['netform'].is_valid():
            forms_dict['netform'].save()
            location = utils.edit_networkinterface_path(request)
            return HttpResponseRedirect(location)
        else:
            #TODO: adicionar mensagem de erro para o usuário
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            return render_to_response(
                'templates/bkp/system/config_networkinterface_module.html',
                return_dict,
                context_instance=RequestContext(request))
