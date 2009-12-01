#!/usr/bin/python
# -*- coding: utf-8 -*-


import re

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm

from environment import ENV
from networkutils import ping, traceroute, resolve_name, resolve_addr, HostAddrNotFound, HostNameNotFound

from backup_corporativo.bkp.utils import redirect, reverse
from backup_corporativo.bkp.models import GlobalConfig, NetworkInterface, Procedure
from backup_corporativo.bkp.forms import NetworkInterfaceEditForm, GlobalConfigForm, OffsiteConfigForm, PingForm, TraceRouteForm, NsLookupForm
from backup_corporativo.bkp.views import global_vars, authentication_required

import logging
logger = logging.getLogger(__name__)

fqn_re = re.compile('^[\w\d.-_]{4,}$')
ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$') 


@authentication_required
def main_system(request):
    E = ENV(request)

    if request.method == 'GET':
        if GlobalConfig.system_configured():
            E.gconfig = GlobalConfig.objects.get(pk=1)
        else:
            E.msg = u"Configure seu sistema."
            location = reverse('edit_system_config')
            return HttpResponseRedirect(location)
        E.iface = NetworkInterface.networkconfig()
        E.template = 'bkp/system/main_system.html'
        return E.render()


@authentication_required
def edit_system_config(request):
    E = ENV(request)

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
    E = ENV(request)

    if request.method == 'POST':
        E.gconfigform = GlobalConfigForm(
            request.POST,
            instance=GlobalConfig()
        )
        if E.gconfigform.is_valid():
            gconf = E.gconfigform.save()
            E.msg = u"Configuração foi alterada com sucesso."
            location = reverse('edit_system_config')
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_config.html'
            return E.render() 


@authentication_required
def manage_system_network(request):
    E = ENV(request)
    
    if request.method == 'GET':
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(instance=E.iface)
        E.pingform = PingForm()
        E.tracerouteform = TraceRouteForm()
        E.nslookupform = NsLookupForm()
        E.template = 'bkp/system/manage_system_network.html'
        return E.render()


@authentication_required
def create_ping(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.pingform = PingForm(request.POST)
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(instance=E.iface)
        E.tracerouteform = TraceRouteForm()
        E.nslookupform = NsLookupForm()
        if E.pingform.is_valid():
            host = E.pingform.cleaned_data['ping_address']
            E.result = ping(host)
        E.template = 'bkp/system/manage_system_network.html'
        return E.render()


@authentication_required
def create_traceroute(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.tracerouteform = TraceRouteForm(request.POST)
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(instance=E.iface)
        E.pingform = PingForm()
        E.nslookupform = NsLookupForm()
        if E.tracerouteform.is_valid():
            host = E.tracerouteform.cleaned_data['traceroute_address']
            E.result = traceroute(host)
        E.template = 'bkp/system/manage_system_network.html'
        return E.render()


@authentication_required
def create_nslookup(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.nslookupform = NsLookupForm(request.POST)
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(instance=E.iface)
        E.pingform = PingForm()
        E.tracerouteform = TraceRouteForm()
        if E.nslookupform.is_valid():
            host = E.nslookupform.cleaned_data['nslookup_address']
            try:
                if re.match(ipv4_re, host):
                    E.result = [resolve_addr(host)]
                elif re.match(fqn_re, host):
                    E.result = [resolve_name(host)]
                else:
                    error = u"Erro de programação: formato inválido de host."
                    raise Exception(error)
            except (HostAddrNotFound, HostNameNotFound):
                error = u"Não foi possível encontrar host: %s" % host
                E.result = [error]
        E.template = 'bkp/system/manage_system_network.html'
        return E.render()


@authentication_required
def update_system_network(request):
    E = ENV(request)

    if request.method == 'POST':
        E.iface = NetworkInterface.networkconfig()
        E.netform = NetworkInterfaceEditForm(request.POST, instance=E.iface)
        if E.netform.is_valid():
            E.netform.save()
            location = reverse('manage_system_network')
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/manage_system_network.html'
            return E.render()


@authentication_required
def edit_system_password(request):
    E = ENV(request)
    
    if request.method == 'GET':
        E.pwdform = PasswordChangeForm(E.current_user)
        E.template = 'bkp/system/edit_system_password.html'
        return E.render()


@authentication_required
def update_system_password(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.pwdform = PasswordChangeForm(E.current_user, request.POST)
        if E.pwdform.is_valid():
            new_pwd = E.pwdform.cleaned_data['new_password1']
            E.current_user.set_password(new_pwd)
            E.current_user.save()
            E.msg = u'Senha alterada com sucesso.'
            logger.info(u'Senha de administrador foi alterada.')
            location = reverse('edit_system_config')
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_password.html'
            return E.render()


@authentication_required
def edit_system_offsite(request):
    E = ENV(request)
    
    if request.method == 'GET':
        E.gconfig = get_object_or_404(GlobalConfig, pk=1)
        E.offsite_on = E.gconfig.offsite_on
        E.offsiteform = OffsiteConfigForm(instance=E.gconfig)
        E.template = 'bkp/system/edit_system_offsite.html'
        return E.render()


@authentication_required
def enable_system_offsite(request):
    E = ENV(request)

    if request.method == 'POST':
        E.gconfig = get_object_or_404(GlobalConfig, pk=1)
        E.offsiteform = OffsiteConfigForm(request.POST, instance=E.gconfig)
        if E.offsiteform.is_valid():
            E.offsiteform.save()
            location = reverse('edit_system_offsite')
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/system/edit_system_offsite.html'
            return E.render()


@authentication_required
def disable_system_offsite(request):
    E = ENV(request)
    
    if request.method == 'POST':
        gconfig = get_object_or_404(GlobalConfig, pk=1)
        gconfig.offsite_on = False
        gconfig.offsite_hour = '00:00:00'
        gconfig.save()
        Procedure.disable_offsite()
        location = reverse('edit_system_offsite')
        return HttpResponseRedirect(location)