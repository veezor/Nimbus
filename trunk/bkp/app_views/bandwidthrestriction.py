#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.models import RestrictionTime
from backup_corporativo.bkp.models import DayOfTheWeek
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
def new_bandwidth_restriction(request):
	vars_dict, forms_dict, return_dict = global_vars(request)

	if request.method == 'GET':
		vars_dict['bandrests'] = BandwidthRestriction.objects.all().order_by('dayoftheweek','restrictiontime')
		forms_dict['bandrest_form'] = BandwidthRestrictionForm()
		return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
		return render_to_response('bkp/new_bandwidthrestriction.html', return_dict, context_instance=RequestContext(request))
	if request.method == 'POST':
		bandrest_form = BandwidthRestrictionForm(request.POST)
		if bandrest_form.is_valid():

			restriction_value = bandrest_form.cleaned_data['restriction_value']
			restriction_time = bandrest_form.cleaned_data['restrictiontime']

			# Verify RestrictionTime
			rest_time = RestrictionTime.objects.filter(restriction_time=restriction_time)
			if not rest_time:# New RestrictionTime
				rest_time = RestrictionTime(restriction_time=restriction_time).save()
			rest_time = RestrictionTime.objects.get(restriction_time=restriction_time)

			for days in bandrest_form.cleaned_data['days']:
				dayoftheweek = DayOfTheWeek.objects.get(day_name=days)
				# Verify BandWidthRestricition
				bandwidthrestriction = BandwidthRestriction.objects.filter(restrictiontime=rest_time,dayoftheweek=dayoftheweek)
				if bandwidthrestriction: # BandWidthRestriction already exists, UPDATE
					bandwidthrestriction = BandwidthRestriction.objects.get(restrictiontime=rest_time,dayoftheweek=dayoftheweek)
					bandwidthrestriction.restriction_value = restriction_value
					bandwidthrestriction.save()
				else: # New BandWidthRestriction
					bandwidthrestriction = BandwidthRestriction(dayoftheweek=dayoftheweek,restrictiontime=rest_time,restriction_value=restriction_value).save()

			request.user.message_set.create(message="Restrição de Banda adicionada com sucesso.")
			return HttpResponseRedirect('/bandwidthrestriction/new')
		else:
			request.user.message_set.create(message="O Formulário contém erros.")
			vars_dict['bandrests'] = BandwidthRestriction.objects.all()
			forms_dict['bandrest_form'] = bandrest_form
			return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
			return render_to_response('bkp/new_bandwidthrestriction.html', return_dict, context_instance=RequestContext(request))

@authentication_required
def delete_bandwidth_restriction(request,bandwidthrestriction_id):
	vars_dict, forms_dict, return_dict = global_vars(request)
	bandwidthrestriction = get_object_or_404(BandwidthRestriction,pk=bandwidthrestriction_id)
	if request.method == 'GET':
		vars_dict['bandwidthrestriction'] = bandwidthrestriction
		return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
		return render_to_response('bkp/delete_confirm_bandwidthrestriction.html', return_dict, context_instance=RequestContext(request))
	if request.method == 'POST':
		request.user.message_set.create(message="Restrição de Banda '%s' removida com sucesso." % bandwidthrestriction)
		bandwidthrestriction.delete()
		return HttpResponseRedirect('/bandwidthrestriction/new')
