#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.network_utils import NetworkInfo
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import GlobalConfig
from backup_corporativo.bkp.forms import NetworkConfigForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

@authentication_required
def edit_network_config(request):
	vars_dict, forms_dict, return_dict = global_vars(request)

	if request.method == 'GET':
		vars_dict['interfaces'] = NetworkInfo.interfaces()
		forms_dict['netform'] = NetworkConfigForm()
		forms_dict['netform'].load_choices()
        # Load forms and vars 
		return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
		return render_to_response('bkp/edit/edit_network_info.html', return_dict, context_instance=RequestContext(request))
        
@authentication_required
def update_network_config(request):
	vars_dict, forms_dict, return_dict = global_vars(request)

	if request.method == 'POST':
		forms_dict['netform'] = NetworkConfigForm(request.POST)
		forms_dict['netform'].load_choices()
        
		if forms_dict['netform'].is_valid():
			forms_dict['netform'].save()
			return HttpResponseRedirect(utils.edit_networkconfig_path(request))
		else:
			vars_dict['interfaces'] = NetworkInfo.interfaces()
			# Load forms and vars 
			return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
			return render_to_response('bkp/edit/edit_network_info.html', return_dict, context_instance=RequestContext(request))
