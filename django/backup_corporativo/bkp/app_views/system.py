#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import ugettext_lazy as _




from environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.utils import redirect, reverse
from backup_corporativo.bkp.models import GlobalConfig, NetworkInterface, Procedure
from backup_corporativo.bkp.forms import NetworkInterfaceEditForm, GlobalConfigForm, OffsiteConfigForm
from backup_corporativo.bkp.views import global_vars, authentication_required

import logging
logger = logging.getLogger(__name__)

@authentication_required
def edit_system_config(request):
    E.update(request)
    E.template = 'bkp/system/edit_system_config.html'
    if request.method == 'GET':
        if GlobalConfig.system_configured():
            E.gconfig = GlobalConfig.objects.get(pk=1)
        else:
            E.gconfig= GlobalConfig()
        E.gconfigform = GlobalConfigForm(instance=E.gconfig)
        return E.render() 



@authentication_required
def update_system_config(request):
    if request.method == 'POST':
        E.update(request)
        E.gconfigform = GlobalConfigForm(
            request.POST,
            instance=GlobalConfig())
        if E.gconfigform.is_valid():
            gconf = E.gconfigform.save()
            E.msg = _("Configuration successfully updated")
            return redirect('edit_system_config')
        else:
            E.template = 'bkp/system/edit_system_config.html'
            return E.render() 

@authentication_required
def edit_system_network(request):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'GET':
        vars_dict['iface'] = NetworkInterface.networkconfig()
        forms_dict['netform'] = NetworkInterfaceEditForm(
            instance=vars_dict['iface'])
        # Load forms and vars 
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/system/edit_system_network.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_system_network(request):
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
                'bkp/system/edit_system_network.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def edit_system_password(request):
    vars_dict, forms_dict = global_vars(request)    
    if request.method == 'GET':
        forms_dict['pwdform'] = PasswordChangeForm(
            vars_dict['current_user'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/system/edit_system_password.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def update_system_password(request):
    vars_dict, forms_dict = global_vars(request)
    if request.method == 'POST':
        forms_dict['pwdform'] = PasswordChangeForm(
            vars_dict['current_user'],
            request.POST)
        if forms_dict['pwdform'].is_valid():
            new_pwd = forms_dict['pwdform'].cleaned_data['new_password1']
            request.user.set_password(new_pwd)
            request.user.save()
            logger.info('Senha alterada com sucesso')
            return HttpResponseRedirect(
                utils.edit_system_config_path(request))
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            return render_to_response(
                'bkp/system/edit_system_password.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def edit_system_offsite(request):
    if request.method == 'GET':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['gconfig'] = get_object_or_404(GlobalConfig, pk=1)
        vars_dict['offsite_on'] = vars_dict['gconfig'].offsite_on
        forms_dict['offsiteform'] = OffsiteConfigForm(
            instance=vars_dict['gconfig'])
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/system/edit_system_offsite.html',
            return_dict,
            context_instance=RequestContext(request))


@authentication_required
def enable_system_offsite(request):
    if request.method == 'POST':
        vars_dict, forms_dict = global_vars(request)
        vars_dict['gconfig'] = get_object_or_404(GlobalConfig, pk=1)
        forms_dict['offsiteform'] = OffsiteConfigForm(
            request.POST,
            instance=vars_dict['gconfig'])
        if forms_dict['offsiteform'].is_valid():
            forms_dict['offsiteform'].save()
            return HttpResponseRedirect(
                utils.edit_system_offsite_path(request))
        else:
            return_dict = utils.merge_dicts(forms_dict, vars_dict)
            return render_to_response(
                'bkp/system/edit_system_offsite.html',
                return_dict,
                context_instance=RequestContext(request))


@authentication_required
def disable_system_offsite(request):
    if request.method == 'POST':
        gconfig = get_object_or_404(GlobalConfig, pk=1)
        gconfig.offsite_on = False
        gconfig.offsite_hour = '00:00:00'
        gconfig.save()
        Procedure.disable_offsite()
        location = utils.edit_system_offsite_path(request)
        return HttpResponseRedirect(location)
