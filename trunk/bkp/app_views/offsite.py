#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import GlobalConfig, Procedure
from backup_corporativo.bkp.forms import OffsiteConfigForm
from backup_corporativo.bkp.views import global_vars, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


@authentication_required
def edit_offsite_config(request):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['gconfig'] = get_object_or_404(GlobalConfig, pk=1)
        vars_dict['offsite_on'] = vars_dict['gconfig'].offsite_on
        forms_dict['offsiteform'] = OffsiteConfigForm(
            instance=vars_dict['gconfig'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/system/config_offsite_feature.html',
            return_dict,
            context_instance=RequestContext(request))

@authentication_required
def enable_offsite(request):
    if request.method == 'POST':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['gconfig'] = get_object_or_404(GlobalConfig, pk=1)
        forms_dict['offsiteform'] = OffsiteConfigForm(
            request.POST,
            instance=vars_dict['gconfig'])
        if forms_dict['offsiteform'].is_valid():
            forms_dict['offsiteform'].save()
            return HttpResponseRedirect(
                utils.edit_offsite_config_path(request))
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            return render_to_response(
                'bkp/system/config_offsite_feature.html',
                return_dict,
                context_instance=RequestContext(request))

@authentication_required
def disable_offsite(request):
    if request.method == 'POST':
        gconfig = get_object_or_404(GlobalConfig, pk=1)
        gconfig.offsite_on = False
        gconfig.offsite_hour = '00:00:00'
        gconfig.save()
        Procedure.disable_offsite()
        location = utils.edit_offsite_config_path(request)
        return HttpResponseRedirect(location)