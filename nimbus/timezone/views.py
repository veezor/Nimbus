#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Create your views here.


import json
from pytz import country_timezones

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from nimbus.timezone.forms import TimezoneForm
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.shared.forms import form, form_mapping
from django.contrib import messages


@login_required
def timezone_conf(request):
    return edit_singleton_model( request, "timezoneconf.html", 
                                 "nimbus.timezone.views.timezone_conf",
                                 formclass = TimezoneForm )


def area_request(request):
    if request.is_ajax() and request.method == 'POST':
        country = request.POST.get('country', {})
        areas = sorted(country_timezones.get(country, []))
        print areas
        response = json.dumps(areas)

        return HttpResponse(response, mimetype="application/json")
