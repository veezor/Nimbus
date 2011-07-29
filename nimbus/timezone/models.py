#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import logging
import time
from operator import itemgetter
from xmlrpclib import ServerProxy


from pytz import country_names

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core.exceptions import ValidationError


from nimbus.shared import signals
from nimbus.libs import systemprocesses
from nimbus.base.models import UUIDSingletonModel as BaseModel


DOMAIN_RE = re.compile(r"^(\w+\.)?\w+\.\w+$")

EMPTY_CHOICES = [('', '----------')]

COUNTRY_CHOICES = [ item \
                    for item in \
                    sorted(country_names.items(), key=itemgetter(1)) ]


def check_domain(value):
    if not DOMAIN_RE.match(value):
        raise ValidationError("ntp_server must be a domain")



class Timezone(BaseModel):
    ntp_server = models.CharField( max_length=255, blank=False,
                                   null=False, default="a.ntp.br",
                                   validators=[check_domain])
    country = models.CharField( max_length=255, blank=False, 
                                choices=COUNTRY_CHOICES)
    area = models.CharField( max_length=255, blank=False, 
                             null=False)


    class Meta:
        verbose_name = u"Fuso horário"


    
class InvalidTimezone(Exception):
    pass


def update_system_timezone(timezone):

    def callable(timezone):
        try:
            server = ServerProxy(settings.NIMBUS_MANAGER_URL)
            server.change_timezone(timezone.area)
            time.tzset()
        except Exception, error:
            logger = logging.getLogger(__name__)
            logger.exception("Conexao com nimbus-manager falhou")


    systemprocesses.norm_priority_job( "Set system timezone", 
                                        callable, timezone)


def update_ntp_cron_file(timezone):

    def callable(timezone):
        try:
            server = ServerProxy(settings.NIMBUS_MANAGER_URL)
            server.generate_ntpdate_file_on_cron(timezone.ntp_server)
        except Exception, error:
            logger = logging.getLogger(__name__)
            logger.exception("Conexao com nimbus-manager falhou")


    systemprocesses.norm_priority_job( "Generate ntpdate cron file", 
                                        callable, timezone)




signals.connect_on( update_system_timezone, Timezone, post_save )
signals.connect_on( update_ntp_cron_file, Timezone, post_save )
