#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.db import models

from nimbus.base.models import BaseModel

import networkutils

class Device(BaseModel):
    name = models.CharField(max_length=255, null=False)
    archive = models.FilePathField()
    storage = models.ForeignKey(Storage, null=False)


class Storage(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.IPAddressField(default="127.0.0.1", null=False, blank=False)
    password = models.CharField( max_length=255, null=False, blank=False,
                                 default=utils.random_password)

    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return "%s (%s:%s)" % (
            self.name,
            self.address) 
