#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Create your views here.


import json
from pytz import country_timezones

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from nimbus.timezone.forms import TimezoneForm
from nimbus.shared.views import edit_singleton_model
from nimbus.wizard.models import add_step
from nimbus.wizard.views import previous_step_url, next_step_url



@add_step(position=3)
def timezone(request):
    extra_context = {
        'wizard_title': u'4 de 5 - Configuração de Hora',
        'page_name': u'timezone',
        'previous': previous_step_url('timezone')
    }
    return edit_singleton_model( request, "generic.html",
                                 next_step_url('timezone'),
                                 formclass = TimezoneForm,
                                 extra_context = extra_context )






@login_required
def timezone_conf(request):
    return edit_singleton_model( request, "timezoneconf.html", 
                                 "nimbus.timezone.views.timezone_conf",
                                 formclass = TimezoneForm )


def area_request(request):
    if request.is_ajax() and request.method == 'POST':
        country = request.POST.get('country', {})
        areas = sorted(country_timezones.get(country, []))
        response = json.dumps(areas)

        return HttpResponse(response, mimetype="application/json")
