#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import datetime
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from nimbus.base.models import SingletonBaseModel
from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.network.models import get_raw_network_interface_address
from nimbus.shared import utils, signals
from nimbus.libs.template import render_to_file


class Config(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    director_name = models.CharField(max_length=255, blank=False, 
                                     null=False, editable=False)
    director_password = models.CharField(max_length=255, 
                                         editable=False,
                                         default=utils.random_password,
                                         blank=False, null=False)
    director_address = models.IPAddressField("nimbus address", null=False,
                                             blank=False,
                                             default=get_raw_network_interface_address)

    def _generate_uuid(self):
        super(Config, self)._generate_uuid()
        if not self.director_name:
            self.director_name = self.uuid.uuid_hex




class BaculaSettings(SingletonBaseModel):
    reload_requests_threshold = models.IntegerField(default=settings.NIMBUS_RELOAD_REQUESTS_THRESHOLD,
                                                    null=False)
    min_reload_requests_interval = models.IntegerField(default=settings.NIMBUS_MIN_RELOAD_REQUESTS_INTERVAL,
                                                       null=False)
    last_bacula_reload = models.DateTimeField(null=True)
    reload_requests_counter = models.IntegerField(default=0, null=True)


    def increment_reload_requests_counter(self):
        self.reload_requests_counter +=1
        self.save()


    def reset_reload_requests_counter(self):
        self.reload_requests_counter = 0
        self.last_bacula_reload = datetime.datetime.now()
        self.save()


    @property
    def has_bacula_reload_requests(self):
        return bool(self.reload_requests_counter)




def update_director_file(config):
    """Generate director file"""
    filename = settings.BACULADIR_CONF
    render_to_file(filename,
                   "bacula-dir",
                   director_name=config.director_name, 
                   director_password=config.director_password,
                   db_name=settings.DATABASES['bacula']['NAME'], 
                   db_user=settings.DATABASES['bacula']['USER'], 
                   db_password=settings.DATABASES['bacula']['PASSWORD'],
                   computers_dir=settings.NIMBUS_COMPUTERS_DIR,
                   filesets_dir=settings.NIMBUS_FILESETS_DIR,
                   jobs_dir=settings.NIMBUS_JOBS_DIR,
                   pools_dir=settings.NIMBUS_POOLS_DIR,
                   schedules_dir=settings.NIMBUS_SCHEDULES_DIR,
                   storages_dir=settings.NIMBUS_STORAGES_DIR)
    logger = logging.getLogger(__name__)
    logger.info("Arquivo de configuracao do director gerado com sucesso")

def update_console_file(config):
    """Update bconsole file"""
    filename = settings.BCONSOLE_CONF
    render_to_file(filename,
                   "bconsole",
                   director_name=config.director_name,
                   director_address=config.director_address,
                   director_password=config.director_password,
                   director_port=9101)
    logger = logging.getLogger(__name__)
    logger.info("Arquivo de configuracao do bconsole gerado com sucesso")

signals.connect_on(update_director_file, Config, post_save)
signals.connect_on(update_console_file, Config, post_save)
