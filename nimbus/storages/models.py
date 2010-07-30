#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import path
import logging

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.conf import settings


import networkutils

from nimbus.base.models import BaseModel
from nimbus.shared import utils, signals, fields
from nimbus.libs.template import render_to_file
from nimbus.config.models import Config







class Storage(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.IPAddressField(default="127.0.0.1", null=False, blank=False)
    password = models.CharField( max_length=255, null=False, blank=False,
                                 default=utils.random_password)

    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return "(%s:%s)" % (
            self.name,
            self.address) 


class Device(BaseModel):
    name = models.CharField(max_length=255, null=False)
    archive = fields.ModelPathField(max_length=1024, null=False, unique=True)
    storage = models.ForeignKey(Storage, null=False)


    def __unicode__(self):
        return "%s in %s" % (self.name, self.archive)



def update_storage_file(storage):
    """Update storage File"""

    filename = settings.BACULASD_CONF 

    if storage.address == "127.0.0.1":
        try:
            logger = logging.getLogger(__name__)

            config = Config.objects.get(id=1)

            render_to_file( filename,
                            "bacula-sd",
                            name=storage.bacula_name,
                            port=9102,
                            max_cur_jobs=100,
                            director_name=config.director_name,
                            director_password=config.director_password)

            logger.info("Arquivo de configuracao do storage gerado com sucesso")
        except Config.DoesNotExist, error:
            logger.info("Config does not exist")


signals.connect_on( update_storage_file, Storage, post_save)


def update_device_file(device):

    name = device.bacula_name

    filename = path.join( settings.NIMBUS_DEVICES_DIR, 
                          name)
    
    storagefile = path.join( settings.NIMBUS_STORAGES_DIR, 
                          name)

    render_to_file( filename,
                    "device",
                    name=name,
                    archive_device=device.archive)

    render_to_file( storagefile,
                    "storages",
                    devices=Device.objects.all())






def remove_device_file(instance):
    name = device.bacula_name

    filename = path.join( settings.NIMBUS_DEVICES_DIR, 
                          name)
    storagefile = path.join( settings.NIMBUS_STORAGES_DIR, 
                          name)

    utils.remove_or_leave(filename)
    utils.remove_or_leave(storagefile)



signals.connect_on( update_device_file, Device, post_save)
signals.connect_on( remove_device_file, Device, post_delete)
