#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import GlobalConfig
from backup_corporativo.bkp.forms import GlobalConfigForm
from backup_corporativo.bkp.forms import RestoreDumpForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Global Config ###
@authentication_required
def edit_config(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    
    try:
        vars_dict['gconfig'] = GlobalConfig.objects.get(pk=1)    
    except GlobalConfig.DoesNotExist:
        vars_dict['gconfig'] = None

    if request.method == 'GET':
        vars_dict['gconfig'] = vars_dict['gconfig'] or GlobalConfig()
        forms_dict['gconfigform'] = GlobalConfigForm(instance=vars_dict['gconfig'])
        forms_dict['restoredumpform'] = RestoreDumpForm()
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/edit_config.html',return_dict, context_instance=RequestContext(request))
    elif request.method == 'POST':
        forms_dict['gconfigform'] = GlobalConfigForm(request.POST, instance=vars_dict['gconfig'])
        forms_dict['restoredumpform'] = RestoreDumpForm()

        if forms_dict['gconfigform'].is_valid():
            vars_dict['gconfig'] = forms_dict['gconfigform'].save()
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Configurações aplicadas com sucesso.")
            return render_to_response('bkp/edit_config.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a configuração não foi alterada.")
            return render_to_response('bkp/edit_config.html', return_dict, context_instance=RequestContext(request))
