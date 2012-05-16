#!/usr/bin/env python
# -*- coding: UTF-8 -*-



from django.http import Http404
from django.utils.translation import ugettext as _

from nimbus.shared.views import render_to_response
from nimbus.wizard.models import add_step
from nimbus.wizard.views import redirect_next_step

@add_step(name="start",position=0)
def license(request):
    extra_context = {
        'wizard_title': _(u'1 of 5 - License'),
        'page_name': u'license',
        'wide': 'wide'
    }
    if request.method == "GET":
        return render_to_response( request, "license.html", extra_context )
    elif request.method == "POST":
        return redirect_next_step('start')
    else:
        raise Http404()


