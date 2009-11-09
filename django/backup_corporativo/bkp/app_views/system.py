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

    if request.method == 'GET':        
        if GlobalConfig.system_configured():
            E.gconfig = GlobalConfig.objects.get(pk=1)
        else:
            E.gconfig= GlobalConfig()
        E.gconfigform = GlobalConfigForm(instance=E.gconfig)
        E.template = 'bkp/system/edit_system_config.html'
        return E.render() 


@authentication_required
def update_system_config(request):
    E.update(request)

    if request.method == 'POST':
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
    E.update(request)
    
    if request.method == 'GET':
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(instance=E.iface)
        E.template = 'bkp/system/edit_system_network.html'
        return E.render()


@authentication_required
def update_system_network(request):
    E.update(request)

    if request.method == 'POST':
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(request.POST, instance=E.iface)
        if E.netform.is_valid():
            E.netform.save()
            # TODO: usar reverse
            location = utils.edit_networkinterface_path(request)
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_network.html'
            return E.render()


@authentication_required
def edit_system_password(request):
    E.update(request)
    
    if request.method == 'GET':
        E.pwdform = PasswordChangeForm(E.current_user)
        E.template = 'bkp/system/edit_system_password.html'
        return E.render()


@authentication_required
def update_system_password(request):
    E.update(request)
    
    if request.method == 'POST':
        E.pwdform = PasswordChangeForm(E.current_user, request.POST)
        if E.pwdform.is_valid():
            new_pwd = E.pwdform.cleaned_data['new_password1']
            E.current_user.set_password(new_pwd)
            E.current_user.save()
            E.msg(_('Senha alterada com sucesso.'))
            logger.info('Senha de administrador foi alterada.')
            # TODO: Usar reverse
            location = utils.edit_system_config_path(request)
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_password.html'
            return E.render()


@authentication_required
def edit_system_offsite(request):
    E.update(request)
    
    if request.method == 'GET':
        E.gconfig = get_object_or_404(GlobalConfig, pk=1)
        E.offsite_on = E.gconfig.offsite_on
        E.offsiteform = OffsiteConfigForm(instance=E.gconfig)
        E.template = 'bkp/system/edit_system_offsite.html'
        return E.render()


@authentication_required
def enable_system_offsite(request):
    E.update(request)

    if request.method == 'POST':
        E.gconfig = get_object_or_404(GlobalConfig, pk=1)
        E.offsiteform = OffsiteConfigForm(request.POST, instance=E.gconfig)
        if E.offsiteform.is_valid():
            E.offsiteform.save()
            # TODO: usar reverse
            location = utils.edit_system_offsite_path(request)
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_offsite.html'
            return E.render()


@authentication_required
def disable_system_offsite(request):
    E.update(request)
    
    if request.method == 'POST':
        gconfig = get_object_or_404(GlobalConfig, pk=1)
        gconfig.offsite_on = False
        gconfig.offsite_hour = '00:00:00'
        gconfig.save()
        Procedure.disable_offsite()
        location = utils.edit_system_offsite_path(request)
        return HttpResponseRedirect(location)