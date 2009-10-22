#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.forms import LoginForm
from backup_corporativo.bkp.models import GlobalConfig
from backup_corporativo.bkp.views import global_vars, authentication_required
# Auth
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404



#TODO: Adicionar comentários ao código.

### Sessions ###
def new_session(request):
    vars_dict, forms_dict = global_vars(request)
    if not request.user.is_authenticated():
        forms_dict['loginform'] = LoginForm()
        return_dict = utils.merge_dicts(forms_dict, vars_dict)
        return render_to_response(
            'bkp/session/new_session.html',
            return_dict,
            context_instance=RequestContext(request))
    else:
        return utils.redirect_back(request)
    

def create_session(request):
    vars_dict, forms_dict = global_vars(request)
    if not request.user.is_authenticated():
        if request.method == 'POST':
            forms_dict['loginform'] = LoginForm(request.POST)
            if forms_dict['loginform'].is_valid():
                auth_login = forms_dict['loginform'].cleaned_data['auth_login']
                auth_passwd = forms_dict['loginform'].cleaned_data['auth_password']
                user = authenticate(username=auth_login, password=auth_passwd)
                if user:
                    login(request, user)
                    if GlobalConfig.system_configured():
                        location = utils.root_path(request)
                        request.user.message_set.create(
                            message="Bem-vindo ao Sistema de Backups Corporativo.")
                    else:
                        location = edit_config_path(request)
                        request.user.message_set.create(
                            message="Configure seu sistema.")
                    return utils.redirect_back(request, default=location)
                else:
                    return_dict = utils.merge_dicts(forms_dict, vars_dict)
                    return render_to_response(
                        'bkp/session/new_session.html',
                        return_dict,
                        context_instance=RequestContext(request))                
            else:
                return_dict = merge_dicts(forms_dict, vars_dict)
                return render_to_response(
                    'bkp/session/new_session.html',
                    return_dict,
                    context_instance=RequestContext(request))
    else:
        return utils.redirect_back(request)

@authentication_required
def delete_session(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            logout(request)
    return HttpResponseRedirect(utils.login_path(request))
