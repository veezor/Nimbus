#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

from nimbus.libs import bacula
from nimbus.wizard import models

class Wizard(object):

    def __init__(self):
        wizard = models.Wizard.get_instance()
        if wizard.has_completed():
            bacula.unlock_bacula_and_start()
            raise MiddlewareNotUsed("wizard completed")
        self.load_steps()

    def process_request(self, request):

        if not self.is_restricted_url(request):
            return None

        wizard = models.Wizard.get_instance()

        if wizard.has_completed():
            return None
        else:
            r = redirect('nimbus.wizard.views.wizard', step="start")
            return r

    def load_steps(self):
        for app in settings.NIMBUS_WIZARD_APPS:
            __import__(app + '.views')

    def is_restricted_url(self, request):
        path = request.META['PATH_INFO']
        if path.startswith("/wizard") or\
                path.startswith("/media") or\
                path.startswith("/recovery") or\
                'ajax' in path:
            return False
        return True
