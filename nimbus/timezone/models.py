#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from operator import itemgetter

from django.db import models
from pytz import country_names


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
