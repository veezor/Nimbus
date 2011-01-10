#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import redirect
from django.contrib import messages



from nimbus.security.models import AdministrativeModel
from nimbus.security.exceptions import AdministrativeModelError


class AdministrativeModelChangeCatcher(object):


    def process_exception(self, request, exception):

        if isinstance(exception, AdministrativeModelError):
            messages.error(request, u"Impossível alterar esse elemento.")
            return redirect(request.META['PATH_INFO'])
