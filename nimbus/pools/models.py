#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from os import path


from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from nimbus.base.models import BaseModel
from nimbus.shared import signals, utils
from nimbus.libs.template import render_to_file


# Create your models here.

class Pool(BaseModel):
    name = models.CharField(max_length=255)
    size = models.FloatField(blank=False, null=False, default=5242880)
    retention_time = models.IntegerField(blank=False, null=False, default=30)

    def __unicode__(self):
        return self.name


def update_pool_file(pool):
    """Pool update pool bacula file""" 

    name = pool.bacula_name

    filename = path.join( settings.NIMBUS_POOLS_DIR, 
                          name)

    render_to_file( filename,
                    "pool",
                    name=name,
                    max_vol_bytes=pool.size,
                    days=pool.retention_time)



def remove_pool_file(pool):
    """pool remove file"""

    name = pool.bacula_name
    filename = path.join( settings.NIMBUS_POOLS_DIR, 
                          name)
    utils.remove_or_leave(filename)


signals.connect_on( update_pool_file, Pool, post_save)
signals.connect_on( remove_pool_file, Pool, post_delete)
