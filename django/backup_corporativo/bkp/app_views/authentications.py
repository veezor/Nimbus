#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from environment import ENV

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.forms import LoginForm
from backup_corporativo.bkp.models import GlobalConfig, Wizard
from backup_corporativo.bkp.views import global_vars, authentication_required


def new_session(request):
    E = ENV(request)
    
    if not E.current_user.is_authenticated():
        E.loginform = LoginForm()
        E.template = 'bkp/session/new_session.html'
        return E.render()
    else:
        location = reverse("main_wizard")
        return HttpResponseRedirect(location)


def create_session(request):
    E = ENV(request)
    
    if not E.current_user.is_authenticated():
        if request.method == 'POST':
            E.loginform = LoginForm(request.POST)
            if E.loginform.is_valid():
                auth_login = E.loginform.cleaned_data['auth_login']
                auth_passwd = E.loginform.cleaned_data['auth_password']
                user = authenticate(username=auth_login, password=auth_passwd)
                if user:
                    login(request, user)
                    if Wizard.get_wizard_lock():
                        location = reverse("list_computers")
                    else:
                        location = reverse("main_wizard")
                    return HttpResponseRedirect(location)
                else:
                    E.template = 'bkp/session/new_session.html'
                    return E.render()
            else:
                E.template = 'bkp/session/new_session.html'
                return E.render()
    else:
        location = reverse("list_computers")
        return HttpResponseRedirect(location)


@authentication_required
def delete_session(request):
    E = ENV(request)
    
    if E.current_user.is_authenticated():
        if request.method == 'POST':
            logout(request)
    location = reverse("new_session")
    return HttpResponseRedirect(location)
