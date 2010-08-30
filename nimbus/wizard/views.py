# Create your views here.
# -*- coding: utf-8 -*-

from functools import wraps

from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import Http404


from nimbus.config.models import Config
from nimbus.network.models import NetworkInterface
from nimbus.timezone.forms import TimezoneForm
from nimbus.offsite.forms import OffsiteForm
from nimbus.shared.views import edit_singleton_model, render_to_response
from nimbus.shared.forms import form
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
def start(request):
    extra_context = {
        'wizard_title': u'1 de 5 - Configuração inicial',
        'page_name': u'start'
    }
    return edit_singleton_model( request, "generic.html", 
                                 "nimbus.wizard.views.timezone",
                                 model = Config,
                                 extra_context = extra_context )

@only_wizard
def timezone(request):
    extra_context = {
        'wizard_title': u'2 de 5 - Configuração de Hora',
        'page_name': u'timezone'
    }
    return edit_singleton_model( request, "generic.html", 
                                 "nimbus.wizard.views.offsite",
                                 formclass = TimezoneForm,
                                 extra_context = extra_context )

@only_wizard
def offsite(request):
    extra_context = {
        'wizard_title': u'3 de 5 -Configuração do Offsite',
        'page_name': u'offsite'
    }
    return edit_singleton_model( request, "generic.html", 
                                 "nimbus.wizard.views.network",
                                 formclass = OffsiteForm,
                                 extra_context = extra_context )

@only_wizard
def network(request):
    extra_context = {
        'wizard_title': u'4 de 5 - Configuração de Rede',
        'page_name': u'network'
    }
    if request.method == "GET":
        interface = NetworkInterface()
        Form = form(NetworkInterface)
        extra_context['form'] = Form(instance=interface)
        return render_to_response( request, "generic.html", extra_context)
    else:
        return edit_singleton_model( request, "generic.html", 
                                     "nimbus.wizard.views.password",
                                     model = NetworkInterface,
                                     extra_context = extra_context )

@only_wizard
def password(request):
    extra_context = {
        'wizard_title': u'5 de 5 - Configuração de Senha',
        'page_name': u'network'
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

    if request.method == "GET":
        wizard = models.Wizard.get_instance()
        wizard.finish()
        return redirect( "nimbus.base.views.home" )

