# Create your views here.
# -*- coding: utf-8 -*-

import logging
from functools import wraps

from django.core.urlresolvers import reverse
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import Http404

from nimbus.network.models import (NetworkInterface, 
                                   get_raw_network_interface_address)
from nimbus.timezone.forms import TimezoneForm
from nimbus.offsite.forms import OffsiteForm
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.shared.forms import form
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


@models.add_step(name="start",position=0)
def license(request):
    extra_context = {
        'wizard_title': u'1 de 5 - Licença',
        'page_name': u'license',
        'wide': 'wide'
    }
    if request.method == "GET":
        return render_to_response( request, "license.html", extra_context )
    elif request.method == "POST":
        return redirect_next_step('start')
    else:
        raise Http404()



@models.add_step(position=1)
def network(request):
    logger = logging.getLogger(__name__)
    extra_context = {'wizard_title': u'2 de 5 - Configuração de Rede',
                     'page_name': u'network'}
    if request.method == "GET":
        interface = NetworkInterface.get_instance()
        Form = form(NetworkInterface)
        extra_context['form'] = Form(instance=interface)
        return render_to_response( request, "generic.html", extra_context)
    else:
        edit_singleton_model(request, "generic.html",
                              next_step_url('network'),
                              model = NetworkInterface,
                              extra_context = extra_context)

        interface = NetworkInterface.get_instance()


        if interface.address == get_raw_network_interface_address():
            return redirect_next_step('network')
        else:
            logger.info('redirecting user to redirect page')
            return render_to_response(request, "redirect.html", 
                                        dict(ip_address=interface.address,
                                             url=next_step_url('network')))


@models.add_step()
def offsite(request):
    extra_context = {'wizard_title': u'3 de 5 - Configuração do Offsite',
                     'page_name': u'offsite',
                     'previous': previous_step_url('offsite')}
    return edit_singleton_model(request, "generic.html",
                                next_step_url('offsite'),
                                formclass = OffsiteForm,
                                extra_context = extra_context)




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



@models.add_step(position=3)
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



@models.add_step(position=-2)
def password(request):
    extra_context = {
        'wizard_title': u'5 de 5 - Senha do usuário admin',
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
            extra_context['messages'] = [u'Please fill all fields.']
            return render_to_response( request, "generic.html", extra_context )
    else:
        raise Http404()


@models.add_step(position=-1)
def finish(request):

    wizard = models.Wizard.get_instance()
    wizard.finish()
    return redirect( "nimbus.base.views.home" )


