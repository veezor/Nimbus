#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import smtplib

from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from nimbus.shared import views
from nimbus.reports.models import EmailConf
from nimbus.reports.forms import EmailConfForm
from nimbus.reports.models import send_hello_message


@login_required
def email_conf(request):
    return views.edit_singleton_model( request, "emailconf.html",
                                 "nimbus.reports.views.email_test",
                                 formclass = EmailConfForm )



@login_required
def email_test(request):
    conf = EmailConf.get_instance()
    if not conf.active:
        messages.warning(request, u"Campo de ativação não selecionado")
        return redirect("nimbus.reports.views.email_conf")
    if request.method == "GET":
        return views.render_to_response(request, "emailtest.html", {})
    elif request.method == "POST":
        try:
            send_hello_message()
            messages.success(request, u"Email enviado corretamente, verifique sua caixa postal")
        except (smtplib.SMTPException, socket.error):
            messages.error(request, u"Impossível enviar email, verifique configurações")
        return redirect('nimbus.reports.views.email_conf')
    else:
        raise Http404()

