#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import redirect
from django.core.exceptions import MiddlewareNotUsed

from nimbus.wizard import views
from nimbus.wizard import models

class Wizard(object):

    def __init__(self):
        wizard = models.Wizard.get_instance()
        if wizard.has_completed():
            raise MiddlewareNotUsed("wizard completed")

    def process_request(self, request):
        wizard = models.Wizard.get_instance()
        
        if wizard.has_completed():
            return None
        else:
            if self.grant_access(request):
                return None
            else:
                return redirect('nimbus.wizard.views.start')

    def grant_access(self, request):
        path = request.META['PATH_INFO']
        if path.startswith("/wizard") or\
                path.startswith("/media") or\
                'ajax' in path:
            return True
    
