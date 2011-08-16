#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import smtplib

from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from nimbus.shared.views import edit_singleton_model
from nimbus.reports.forms import EmailConfForm
from nimbus.reports.models import send_hello_message


@login_required
def email_conf(request):
    return edit_singleton_model( request, "emailconf.html",
                                 "nimbus.reports.views.email_conf",
                                 formclass = EmailConfForm )



@login_required
def email_test(request):
    if request.method == "POST":
        try:
            send_hello_message()
            messages.sucesss(u"Email enviado corretamente, verifique sua caixa postal")
        except smtplib.SMTPException:
            messages.error(u"Impossível enviar email, verifique configurações")
        return redirect('nimbus.reports.views.email_conf')
    else:
        raise Http404()

