#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import GlobalConfig, Procedure
from backup_corporativo.bkp.models import ExternalDevice
from backup_corporativo.bkp.forms import GlobalConfigForm, OffsiteConfigForm
from backup_corporativo.bkp.forms import RestoreDumpForm
from backup_corporativo.bkp.forms import ExternalDeviceForm
from backup_corporativo.bkp.forms import ExternalDeviceEditForm
from django.contrib.auth.forms import PasswordChangeForm
from backup_corporativo.bkp.models import RestrictionTime
from backup_corporativo.bkp.models import DayOfTheWeek
from backup_corporativo.bkp.models import BandwidthRestriction
from backup_corporativo.bkp.models import RestrictionTime
from backup_corporativo.bkp.forms import BandwidthRestrictionForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Global Config ###
@authentication_required
def edit_config(request, config_type='global'):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    vars_dict['config_type'] = config_type
    vars_dict['request'] = request
    try:
        vars_dict['gconfig'] = GlobalConfig.objects.get(pk=1)    
    except GlobalConfig.DoesNotExist:
        vars_dict['gconfig'] = None

    if request.method == 'GET':
        if config_type:
            if config_type == 'global':
                vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
                forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
            elif config_type == 'password':
                forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'])
            elif config_type == 'offsite':
                vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
                vars_dict['offsite_on'] = vars_dict['gconfig'].offsite_on
                if vars_dict['offsite_on']:
                    vars_dict['procedures'] = Procedure.objects.filter(offsite_on=True)
        else:
            vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
            forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
            # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit/edit_config.html',return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['gconfigform'] = GlobalConfigForm(request.POST, instance=vars_dict['gconfig'])

        if forms_dict['gconfigform'].is_valid():
            vars_dict['gconfig'] = forms_dict['gconfigform'].save()
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Configurações aplicadas com sucesso.")
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a configuração não foi alterada.")
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))


### Password Management ###
@authentication_required
def change_password(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    if request.method == 'POST':
        forms_dict['pwdform'] = PasswordChangeForm(return_dict['current_user'], request.POST)
        
        if forms_dict['pwdform'].is_valid():
            request.user.set_password(forms_dict['pwdform'].cleaned_data['new_password1'])
            request.user.save()
            request.user.message_set.create(message="Senha foi alterada com sucesso.")
            return redirect_back_or_default(request, default=root_path(request))
        else:
            vars_dict['config_type'] = 'password'
            # Load forms and vars
            request.user.message_set.create(message="Houve um erro e a senha não foi alterada.")
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))

@authentication_required
def edit_offsite(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    if request.method == 'GET':
        return HttpResponseRedirect(edit_offsite_path(request))
    
    if request.method == 'POST':
        global_config = GlobalConfig.objects.get(pk=1)
        forms_dict['offsiteform'] = OffsiteConfigForm(request.POST, instance=global_config)
        
        if forms_dict['offsiteform'].is_valid():
            forms_dict['offsiteform'].save()
            request.user.message_set.create(message="Dados do backup offsite alterados com sucesso.")
            return HttpResponseRedirect(edit_offsite_path(request))
        else:
            vars_dict['config_type'] = 'offsite'
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Houve um erro ao tentar alterar os dados do backup offsite.")
            #return HttpResponseRedirect(new_offsite_path(request))
            return render_to_response('bkp/edit/edit_config.html', return_dict, context_instance=RequestContext(request))

