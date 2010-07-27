#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models
from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.shared import utils

class Config(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    director_name = models.CharField(max_length=255, blank=False, null=False)
    director_password = models.CharField( max_length=255, 
                                          default=utils.random_password,
                                          blank=False, null=False)

