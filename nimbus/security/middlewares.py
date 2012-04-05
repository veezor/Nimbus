#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import redirect
from django.contrib import messages

from nimbus.security.exceptions import AdministrativeModelError
from django.utils.translation import ugettext as _


class AdministrativeModelChangeCatcher(object):


    def process_exception(self, request, exception):

        if isinstance(exception, AdministrativeModelError):
            messages.error(request, _(u"Access denied."))
            return redirect(request.META['PATH_INFO'])
