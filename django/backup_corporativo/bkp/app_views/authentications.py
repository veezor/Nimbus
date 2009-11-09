#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from Environment import ENV as E

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.forms import LoginForm
from backup_corporativo.bkp.models import GlobalConfig
from backup_corporativo.bkp.views import global_vars, authentication_required


def new_session(request):
    E.update(request)
    
    if not E.current_user.is_authenticated():
        E.loginform = LoginForm()
        E.template = 'bkp/session/new_session.html'
        return E.render()
    else:
        return utils.redirect_back(request)    


def create_session(request):
    E.update(request)
    
    if not E.current_user.is_authenticated():
        if request.method == 'POST':
            E.loginform = LoginForm(request.POST)
            if E.loginform.is_valid():
                auth_login = E.loginform.cleaned_data['auth_login']
                auth_passwd = E.loginform.cleaned_data['auth_password']
                user = authenticate(username=auth_login, password=auth_passwd)
                if user:
                    login(request, user)
                    if GlobalConfig.system_configured():
                        location = utils.root_path(request)
                        E.msg = _("Bem-vindo ao Sistema de Backups Corporativo.")
                    else:
                        location = edit_config_path(request)
                        E.msg = _("Configure seu sistema.")
                    return utils.redirect_back(request, default=location)
                else:
                    E.template = 'bkp/session/new_session.html'
                    return E.render()
            else:
                E.template = 'bkp/session/new_session.html'
                return E.render()
    else:
        return utils.redirect_back(request)


@authentication_required
def delete_session(request):
    E.update(request)
    
    if E.current_user.is_authenticated():
        if request.method == 'POST':
            logout(request)
    return HttpResponseRedirect(utils.login_path(request))
