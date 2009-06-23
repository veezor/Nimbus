#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import BandwidthRestriction
from backup_corporativo.bkp.forms import BandwidthRestrictionForm
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

### Bandwidth Restriction ###
@authentication_required
def new_restriction(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['rests'] = BandwidthRestriction.objects.all()

    if request.method == 'GET':
        forms_dict['restform'] = BandwidthRestrictionForm()
        # Load forms and vars
        return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
        return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
        
@authentication_required
def create_restriction(request):
    vars_dict, forms_dict, return_dict = global_vars(request)
    vars_dict['rests'] = BandwidthRestriction.objects.all()
    
    if request.method == 'POST':
        forms_dict['restform'] = BandwidthRestrictionForm(request.POST)
        
        if forms_dict['restform'].is_valid():
            try:
                rest =  forms_dict['restform'].save()
                request.user.message_set.create(message="Restrição cadastrada com sucesso.")
                return HttpResponseRedirect("%s/restriction/new" % (request.META['SCRIPT_NAME']))
            except Exception:
                return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
                request.user.message_set.create(message="O limite de restrições cadastradas foi atingido e a restrição não foi adicionada.")
                return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
        else:
            # Load forms and vars
            return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
            request.user.message_set.create(message="Existem erros e a restrição não foi cadastrada.")
            return render_to_response('bkp/new_restriction.html', return_dict, context_instance=RequestContext(request))
