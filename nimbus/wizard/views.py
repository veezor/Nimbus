# Create your views here.
# -*- coding: utf-8 -*-

from functools import wraps

from django.core.urlresolvers import reverse

from django.shortcuts import redirect
from django.http import Http404

from nimbus.shared.views import render_to_response

from nimbus.wizard import models


def only_wizard(view):
    @wraps(view)
    def wrapper(request, step):
        wizard = models.Wizard.get_instance()
        if wizard.has_completed():
            raise Http404()
        else:
            return view(request, step)

    return wrapper



@only_wizard
def wizard(request, step):
    current = step
    step = models.wizard_manager.get_step(step)
    return step(request)



@only_wizard
def wizard_previous(request, step):
    return redirect_previous_step(step)

@only_wizard
def wizard_next(request, step):
    return redirect_next_step(step)

def redirect_next_step(current):
    stepname, step = models.wizard_manager.get_next_step(current)
    return redirect('nimbus.wizard.views.wizard', step=stepname)

def redirect_previous_step(current):
    stepname, step = models.wizard_manager.get_previous_step(current)
    return redirect('nimbus.wizard.views.wizard', step=stepname)

def previous_step_url(current):
    return reverse('nimbus.wizard.views.wizard_previous', kwargs={"step":current})

def next_step_url(current):
    return reverse('nimbus.wizard.views.wizard_next', kwargs={"step":current})




@only_wizard
def recovery(request):
    extra_context = {
        'wizard_title': u'Recuperação do sistema',
        'page_name': u'recovery',
        'next': reverse('nimbus.wizard.views.timezone')
    }
    if request.method == "GET":
        return render_to_response( request, "recovery.html", extra_context )
    elif request.method == "POST":
        return redirect('nimbus.recovery.views.select_source')
    else:
        raise Http404()



@models.add_step(position=-1)
def finish(request):

    wizard = models.Wizard.get_instance()
    wizard.finish()
    return redirect( "nimbus.base.views.home" )


