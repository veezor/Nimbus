#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response as _render_to_response
from django.shortcuts import get_object_or_404
from django.views.generic import list_detail
from django.views.generic.simple import  direct_to_template


from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp.models import Wizard


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



def default_context_processor(request):
    """ A context processor that provider request, script_name,
        current_user and current_time """
    return { 
      "request" : request,
      "script_name" : request.META['SCRIPT_NAME'],
      "current_user" : request.user,
      "current_time" : utils.current_time()
    }




def require_authentication(request):
    """Redirect user to authentication page."""
    return HttpResponseRedirect(utils.reverse('new_session'))


def authentication_required(view_def):
    """Decorator to force a view to verify if user is authenticated."""
    def check_auth(*args, **kw):
        if not args[0].user.is_authenticated():
            return require_authentication(args[0])


        view_name = view_def.func_name
        redirect = not 'wizard' in view_name and view_name != 'delete_session'

        if not Wizard.has_completed() and redirect:
            return HttpResponseRedirect(utils.reverse('main_wizard'))
        
        return view_def(*args, **kw)
    check_auth.__name__ = view_def.__name__
    check_auth.__doc__ = view_def.__doc__
    return check_auth


@authentication_required
def restricted_object_list(*args, **kwargs):
    return list_detail.object_list(*args, **kwargs)



@authentication_required
def restricted_object_detail(*args, **kwargs):
    return list_detail.object_detail(*args, **kwargs)


@authentication_required
def restricted_direct_to_template(*args, **kwargs):
    return direct_to_template(*args, **kwargs)


def make_list_generic_view_dict(template, queryset):
    return {
        "template_name" : template,
        "queryset" : queryset,
        "paginate_by" : 25,
        "context_processors" : [default_context_processor]}


###
### Templates
###

def render(request, template_name, dictionary):
    return _render_to_response( template_name, dictionary,
                                context_instance=RequestContext(request,
                                processors = [default_context_processor]))



def make_method_handler(method_name):

    def handler(function):

        @authentication_required
        def wrapper(request, *args, **kwargs):
            if request.method == method_name.upper():
                return function(request, *args, **kwargs)
            else:
                raise Http404()

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        wrapper.__dict__ = function.__dict__

        return wrapper

    handler.__name__ = method_name
    return handler


allow_post = make_method_handler("post")
allow_get = make_method_handler("get")

# External views
from backup_corporativo.bkp.app_views.management import *
from backup_corporativo.bkp.app_views.system import *
from backup_corporativo.bkp.app_views.authentications import *
from backup_corporativo.bkp.app_views.computers import *
from backup_corporativo.bkp.app_views.computeraddrequest import *
from backup_corporativo.bkp.app_views.filesets import *
from backup_corporativo.bkp.app_views.procedures import *
from backup_corporativo.bkp.app_views.schedules import *
from backup_corporativo.bkp.app_views.stats import *
from backup_corporativo.bkp.app_views.tmp_restores import *
from backup_corporativo.bkp.app_views.externalstorages import *
from backup_corporativo.bkp.app_views.offsite import *

from backup_corporativo.bkp.app_views.wizard import *
from backup_corporativo.bkp.app_views.recovery import *
