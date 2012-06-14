#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import socket
import smtplib

from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from nimbus.shared import views
from nimbus.reports.forms import EmailConfForm
from nimbus.reports.models import send_hello_message


@login_required
def email_conf(request):
    return views.edit_singleton_model( request, "emailconf.html",
                                 "nimbus.reports.views.email_test",
                                 formclass = EmailConfForm )



@login_required
def email_test(request):
    if request.method == "GET":
        return views.render_to_response(request, "emailtest.html", {})
    elif request.method == "POST":
        try:
            send_hello_message()
            messages.success(request, _(u"Email sent correctly, check your mailbox"))
        except (smtplib.SMTPException, socket.error):
            messages.error(request, _(u"Unable to send email, check configuration"))
        return redirect('nimbus.reports.views.email_conf')
    else:
        raise Http404()

