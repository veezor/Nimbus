#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, DAYS_OF_THE_WEEK


###
###   Decorators and Global Definitions
###

# ATENÇÃO!
# Favor não declarar formulários dentro da variável 
# forms_dict dessa função. O motivo para isso é que em várias
# partes do código do Nimbus o seguinte trecho é utilizado
# "if all([form.is_valid() for form in forms_dict.values()])"
# e um formulário incluído aqui fará com que esse código
# se comporte de forma estranha, já que existirá um formulário
# vazio presente em forms_dict.values()
def global_vars(request):
    """Declare system-wide variables."""
    vars_dict = {}
    forms_dict = {}
    vars_dict['script_name'] = request.META['SCRIPT_NAME']
    vars_dict['current_user'] = request.user
    # Lista de computadores e storages.
    vars_dict['comps'] = Computer.objects.all()
    # Algumas variáveis importantes.
    vars_dict['TYPE_CHOICES'] = TYPE_CHOICES
    vars_dict['LEVEL_CHOICES'] = LEVEL_CHOICES
    vars_dict['DAYS_OF_THE_WEEK'] = DAYS_OF_THE_WEEK
    # TODO: verificar se é realmente necessário enviar request inteiro
    # em TODAS as views.
    vars_dict['request'] = request
    
    return vars_dict, forms_dict        


def require_authentication(request):
    """Redirect user to authentication page."""
    return HttpResponseRedirect(utils.login_path(request))


def authentication_required(view_def):
    """Decorator to force a view to verify if user is authenticated."""
    def check_auth(*args, **kw):
        if not args[0].user.is_authenticated():
            return require_authentication(args[0])
        return view_def(*args, **kw)
    check_auth.__name__ = view_def.__name__
    check_auth.__doc__ = view_def.__doc__
    return check_auth


# External views
from backup_corporativo.bkp.app_views.management import *
from backup_corporativo.bkp.app_views.authentications import *
from backup_corporativo.bkp.app_views.computers import *
from backup_corporativo.bkp.app_views.configs import *
from backup_corporativo.bkp.app_views.filesets import *
from backup_corporativo.bkp.app_views.procedures import *
from backup_corporativo.bkp.app_views.schedules import *
from backup_corporativo.bkp.app_views.storages import *
from backup_corporativo.bkp.app_views.stats import *
from backup_corporativo.bkp.app_views.tmp_restores import *
from backup_corporativo.bkp.app_views.wizbkp import *
from backup_corporativo.bkp.app_views.networkinterfaces import *
from backup_corporativo.bkp.app_views.offsite import *
from backup_corporativo.bkp.app_views.tools import *
