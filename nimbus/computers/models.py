#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from nimbus.bacula.models import Job, Client
from nimbus.base.models import BaseModel
from nimbus.config.models import Config
from nimbus.shared import utils, enums, signals
from nimbus.libs.template import render_to_file, render_to_string


OS = ( (os,os) for os in enums.operating_systems)


class UnableToGetFile(Exception):
    pass




class ComputerGroup(models.Model):
    name = models.CharField( max_length=255, unique=True, 
                             blank=False, null=False)

    def __unicode__(self):
        return self.name


class Computer(BaseModel):

    name = models.CharField( max_length=255, unique=True, 
                             blank=False, null=False)
    address = models.IPAddressField(blank=False, null=False)
    operation_system = models.CharField( max_length=255,
                                         blank=False, null=False,
                                         choices=OS )
    description = models.TextField( max_length=1024, blank=True)
    password = models.CharField( max_length=255,
                                 blank=False, null=False,
                                 editable=False,
                                 default=utils.random_password)
    groups = models.ManyToManyField(ComputerGroup, related_name="computers",
                                    blank=True, null=True)



    def _get_crypt_file(self, filename):
        km = KeyManager()
        client_path = km.get_client_path(self.name)
        path = os.path.join(client_path, file_name)
        try:
            file_content = open(file_path, 'r') 
            file_read = file_content.read()
            file_content.close()
            return file_read
        except IOError, e:
            raise UnableToGetFile("Original error was: %s" % e)      


    def get_pem(self):
        return self._get_crypt_file("client.pem")


    def get_config_file(self):
        config = Config.get_instance()
        return render_to_string("bacula-fd", 
                                director_name=config.director_name,
                                password=self.password,
                                name=self.bacula_name,
                                os=self.operating_systems,
                                nimbus=False)


    @property
    def bacula_id(self):
        return Client.objects.get(name=self.bacula_name).clientid

    def successful_jobs(self):
        return Job.objects.filter( jobstatus__in=('T','W'), 
                             client__name=self.bacula_name)\
                                     .order_by('endtime').distinct()[:15]

    def unsuccessful_jobs(self):
        return Job.objects.filter( jobstatus__in=('E','e','f','I'), 
                             client__name=self.bacula_name)\
                                     .order_by('endtime').distinct()[:15]

    def running_jobs(self):
        status = ('R','p','j','c','d','s','M','m','s','F','B')
        return Job.objects.filter( jobstatus__in=status, 
                             client__name=self.bacula_name)\
                                     .order_by('starttime').distinct()[:5]


    def last_jobs(self):
        return Job.objects.filter(client__name=self.bacula_name)\
                                .order_by('endtime').distinct()[:15]

    def __unicode__(self):
       return "%s (%s)" % (self.name, self.address)



def update_computer_file(computer):
    """Computer update file"""

    name = computer.bacula_name


    filename = path.join( settings.NIMBUS_COMPUTERS_DIR, 
                          name)

    render_to_file( filename,
                    "client",
                    name=name,
                    ip=computer.address,
                    password=computer.password)



def remove_computer_file(computer):
    """Computer remove file"""

    filename = path.join( settings.NIMBUS_COMPUTERS_DIR, 
                          computer.bacula_name)
    utils.remove_or_leave(filename)



signals.connect_on( update_computer_file, Computer, post_save)
signals.connect_on( remove_computer_file, Computer, post_delete)
