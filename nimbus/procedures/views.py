# -*- coding: utf-8 -*-
# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.procedures.models import Procedure
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form


def list(request):
    procedures = Procedure.objects.all()
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos"
    }
    return render_to_response(request, "procedures_list.html", extra_content)


def list_offsite(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos com offsite ativo"
    }
    return render_to_response(request, "procedures_list.html", extra_content)
