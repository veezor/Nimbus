#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import logging
from operator import itemgetter
from xmlrpclib import ServerProxy


from pytz import country_names

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

from nimbus.shared import signals
from nimbus.base.models import UUIDSingletonModel as BaseModel


EMPTY_CHOICES = [('', '----------')]

COUNTRY_CHOICES = [ item \
                    for item in \
                    sorted(country_names.items(), key=itemgetter(1)) ]



class Timezone(BaseModel):
    ntp_server = models.CharField( max_length=255, blank=False,
                                   null=False, default="a.ntp.br")
    country = models.CharField( max_length=255, blank=False, 
                                choices=COUNTRY_CHOICES)
    area = models.CharField( max_length=255, blank=False, 
                             null=False,
                             choices=EMPTY_CHOICES, 
                             default=('', '----------'))

    
class InvalidTimezone(Exception):
    pass


def update_system_timezone(timezone):
    try:
        server = ServerProxy(settings.NIMBUS_MANAGER_URL)
        server.change_timezone(timezone.area)
    except Exception, error:
        logger = logging.getLogger(__name__)
        logger.exception("Conexao com nimbus-manager falhou")



signals.conncect_on( update_system_timezone, Timezone, post_save )