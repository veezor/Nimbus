#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.http import Http404, HttpResponse
from django.db import IntegrityError


from backup_corporativo.bkp.models import (OS_CHOICES, 
                                           ComputerAddRequest)



def autoaddcomputer(request):
    if request.method == "POST":
        choices = [  item[0] for item in OS_CHOICES ]
        try:
            os = request.POST['os']
            if os not in choices:
                return HttpResponse(status=400)
            
            name = request.META['REMOTE_HOST']
            if name == '':
                name = u"Ausente"

            computer = ComputerAddRequest(name = name,
                                          ip = request.META['REMOTE_ADDR'],
                                          operation_system=os)
            computer.save()
            return HttpResponse(status=200)
        except (KeyError, IntegrityError), e:
            return HttpResponse(status=400)
    else:
        raise Http404()
