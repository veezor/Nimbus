#!/usr/bin/env python
# -*- coding: UTF-8 -*-




from django.http import Http404
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from nimbus.shared.views import render_to_response
from nimbus.wizard.models import add_step
from nimbus.wizard.views import redirect_next_step, previous_step_url

@add_step(position=-2)
def password(request):
    extra_context = {
        'wizard_title': _(u'5 of 5 - Admin password'),
        'page_name': u'password',
        'previous': previous_step_url('password')
    }
    user = User.objects.get(id=1)
    if request.method == "GET":
        extra_context['form'] = SetPasswordForm(user)
        return render_to_response( request, "generic.html", extra_context )
    elif request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect_next_step('password')
        else:
            extra_context['form'] = SetPasswordForm(user)
            extra_context['messages'] = [_(u'Please fill all fields.')]
            return render_to_response( request, "generic.html", extra_context )
    else:
        raise Http404()


