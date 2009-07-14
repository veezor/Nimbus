#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO:
# Falta tratar erros URL caso o ID esteja faltando 
# Validar gatilho c/ tipo de agendamento

# Application
from backup_corporativo.bkp.utils import *
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
import os
# Vars
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, DAYS_OF_THE_WEEK


###
###   Decorators and Global Definitions
###

def global_vars(request):
    """Declare system-wide variables."""
    vars_dict = {}; forms_dict = {}; return_dict = {}
    return_dict['script_name'] = request.META['SCRIPT_NAME']
    return_dict['current_user'] = request.user
    # List of computers.
    vars_dict['comps'] = Computer.objects.all()
    # List of forms has been removed! 
    # (Please declare only forms the views)
    # List of vars.    
    vars_dict['TYPE_CHOICES'] = TYPE_CHOICES
    vars_dict['LEVEL_CHOICES'] = LEVEL_CHOICES
    vars_dict['DAYS_OF_THE_WEEK'] = DAYS_OF_THE_WEEK
    
    return vars_dict, forms_dict, return_dict


def require_authentication(request):
    """Redirect user to authentication page."""
    return HttpResponseRedirect(login_path(request))


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
from backup_corporativo.bkp.app_views.authentications import *
from backup_corporativo.bkp.app_views.computers import *
from backup_corporativo.bkp.app_views.configs import *
from backup_corporativo.bkp.app_views.dumps import *
from backup_corporativo.bkp.app_views.filesets import *
from backup_corporativo.bkp.app_views.procedures import *
from backup_corporativo.bkp.app_views.schedules import *
from backup_corporativo.bkp.app_views.stats import *
from backup_corporativo.bkp.app_views.triggers import *
from backup_corporativo.bkp.app_views.tmp_restores import *
