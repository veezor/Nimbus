#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import logging

from django.contrib.auth.decorators import login_required

from nimbus.shared.views import render_to_response
from nimbus.network.models import NetworkInterface, get_raw_network_interface_address
from nimbus.network.forms import NetworkForm
from nimbus.shared.views import edit_singleton_model
from nimbus.shared.utils import project_port
from nimbus.wizard.models import add_step
from nimbus.wizard.views import next_step_url, redirect_next_step
from nimbus.shared.forms import form


@add_step(position=1)
def network(request):
    logger = logging.getLogger(__name__)
    extra_context = {'wizard_title': u'2 de 5 - Configuração de Rede',
                     'page_name': u'network'}
    if request.method == "GET":
        interface = NetworkInterface.get_instance()
        extra_context['form'] = NetworkForm(instance=interface)
        return render_to_response( request, "generic.html", extra_context)
    else:
        response = edit_singleton_model(request, "generic.html",
                                        next_step_url('network'),
                                        formclass = NetworkForm,
                                        extra_context = extra_context)
                           

        if response.status_code == 200:
            return response
            
                                                  

        interface = NetworkInterface.get_instance()


        if interface.address == get_raw_network_interface_address():
            return redirect_next_step('network')
        else:
            logger.info('redirecting user to redirect page')
            return render_to_response(request, "redirect.html", 
                                        dict(ip_address=interface.address,
                                             url=next_step_url('network')))



@login_required
def network_conf(request):
    return edit_singleton_model(request, "myform.html", 
                                 "nimbus.network.views.redirect_after_update",
                                 model = NetworkInterface )

@login_required
def redirect_after_update(request):
    ni = NetworkInterface.objects.all()[0]
    port = project_port(request)
    ip_address = ni.address + port
    return render_to_response(request, 'redirect.html', locals())
