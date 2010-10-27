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
from nimbus.computers.models import Computer







class Storage(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.IPAddressField(default="127.0.0.1", editable=False, 
                                    null=False, blank=False)
    password = models.CharField( max_length=255, null=False, 
                                 blank=False, editable=False,
                                 default=utils.random_password)

    description = models.TextField(max_length=500, blank=True)
    active = models.BooleanField(editable=False)


    @property
    def is_local(self):
        if self.address == "127.0.0.1":
            return True
        return False
        

    def __unicode__(self):
        return u"(%s:%s)" % (
            self.name,
            self.address)
    
    @property
    def get_computers(self):
        """Computadores que fazem backup neste storage."""
        computers = Computer.objects.filter(procedure__profile__storage=self).\
            order_by('name').distinct()
        
        # computers = []
        # for profile in self.profile_set.all():
        #     for procedure in profile.procedure_set.all():
        #         computers.append(procedure.computer)
        # 
        # sorted(computers, key=lambda computer: computer.name)
        return computers


class Device(BaseModel):
    name = models.CharField(max_length=255, null=False)
    archive = fields.ModelPathField(max_length=255, null=False, unique=True)
    storage = models.ForeignKey(Storage, null=False, related_name="devices")

    @property
    def is_local(self):
        return self.storage.is_local


    def __unicode__(self):
        return "%s in %s" % (self.name, self.archive)



def update_storage_file(storage):
    """Update storage File"""

    filename = settings.BACULASD_CONF 

    if storage.is_local and storage.active:
        try:
            logger = logging.getLogger(__name__)

            config = Config.objects.get(id=1)

            render_to_file( filename,
                            "bacula-sd",
                            name=storage.bacula_name,
                            port=9102,
                            max_cur_jobs=100,
                            director_name=config.director_name,
                            director_password=config.director_password,
                            devices_dir=settings.NIMBUS_DEVICES_DIR)

            logger.info("Arquivo de configuracao do storage gerado com sucesso")
        except Config.DoesNotExist, error:
            logger.info("Config does not exist")




def create_default_device(storage):

    if storage.devices.count() == 0:
        device = Device.objects.create(name="device default",
                                       archive="/bacula/",
                                       storage=storage)
        storage.devices.add(device)


def update_device_file(device):

    if device.storage.active:

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






def remove_device_file(device):

    if device.storage.active:
        name = device.bacula_name

        filename = path.join( settings.NIMBUS_DEVICES_DIR, 
                              name)
        storagefile = path.join( settings.NIMBUS_STORAGES_DIR, 
                              name)

        utils.remove_or_leave(filename)
        utils.remove_or_leave(storagefile)



signals.connect_on( update_storage_file, Storage, post_save)
signals.connect_on( create_default_device, Storage, post_save)
signals.connect_on( update_device_file, Device, post_save)
signals.connect_on( remove_device_file, Device, post_delete)
