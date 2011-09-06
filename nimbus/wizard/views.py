# Create your views here.
# -*- coding: utf-8 -*-

import logging
from functools import wraps

from django.core.urlresolvers import reverse
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import Http404

from nimbus.config.models import Config
from nimbus.network.models import (NetworkInterface, 
                                   get_raw_network_interface_address)
from nimbus.timezone.forms import TimezoneForm
from nimbus.offsite.forms import OffsiteForm
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.shared.forms import form
from nimbus.shared.utils import project_port
from nimbus.wizard import models


def only_wizard(view):
    @wraps(view)
    def wrapper(request):
        wizard = models.Wizard.get_instance()
        if wizard.has_completed():
            raise Http404()
        else:
            return view(request)

    return wrapper

@only_wizard
def license(request):
    extra_context = {
        'wizard_title': u'1 de 5 - Licença',
        'page_name': u'license',
        'wide': 'wide'
    }
    if request.method == "GET":
        return render_to_response( request, "license.html", extra_context )
    elif request.method == "POST":
        return redirect('nimbus.wizard.views.network')
    else:
        raise Http404()



@only_wizard
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
                             "nimbus.wizard.views.offsite",
                              model = NetworkInterface,
                              extra_context = extra_context)

        interface = NetworkInterface.get_instance()


        if interface.address == get_raw_network_interface_address():
            return redirect( "nimbus.wizard.views.offsite" )
        else:
            logger.info('redirecting user to redirect page')
            return render_to_response(request, "redirect.html", 
                                        dict(ip_address=interface.address,
                                             url=reverse('nimbus.wizard.views.offsite')))


@only_wizard
def offsite(request):
    extra_context = {'wizard_title': u'3 de 5 - Configuração do Offsite',
                     'page_name': u'offsite',
                     'previous': reverse('nimbus.wizard.views.network')}
    return edit_singleton_model(request, "generic.html",
                                "nimbus.wizard.views.recovery",
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



@only_wizard
def timezone(request):
    extra_context = {
        'wizard_title': u'4 de 5 - Configuração de Hora',
        'page_name': u'timezone',
        'previous': reverse('nimbus.wizard.views.recovery')
    }
    return edit_singleton_model( request, "generic.html",
                                 "nimbus.wizard.views.password",
                                 formclass = TimezoneForm,
                                 extra_context = extra_context )



@only_wizard
def password(request):
    extra_context = {
        'wizard_title': u'5 de 5 - Senha do usuário admin',
        'page_name': u'password',
        'previous': reverse('nimbus.wizard.views.timezone')
    }
    user = User.objects.get(id=1)
    if request.method == "GET":
        extra_context['form'] = SetPasswordForm(user)
        return render_to_response( request, "generic.html", extra_context )
    elif request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('nimbus.wizard.views.finish')
        else:
            extra_context['form'] = SetPasswordForm(user)
            extra_context['messages'] = [u'Please fill all fields.']
            return render_to_response( request, "generic.html", extra_context )
    else:
        raise Http404()


@only_wizard
def finish(request):

    #GET OR POST
    wizard = models.Wizard.get_instance()
    wizard.finish()

    network_interface = NetworkInterface.get_instance()
    if network_interface.address == get_raw_network_interface_address():
        return redirect( "nimbus.base.views.home" )
    else:
        network_interface.save() # change ip address
        return render_to_response(request, "redirect.html", dict(ip_address=network_interface.address,
                                                                 url="/"))

