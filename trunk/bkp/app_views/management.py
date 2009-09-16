#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Storage
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

@authentication_required
def view_management(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_management.html', return_dict, context_instance=RequestContext(request))
        
@authentication_required
def view_computers(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_computers.html', return_dict, context_instance=RequestContext(request))

@authentication_required
def view_storages(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'GET':
        return_dict = utils.merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/view/view_storages.html', return_dict, context_instance=RequestContext(request))
