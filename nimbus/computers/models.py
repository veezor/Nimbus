#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import path
import xmlrpclib
import keymanager

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save

from nimbus.bacula.models import Job, Client
from nimbus.base.models import BaseModel
from nimbus.config.models import Config
from nimbus.shared import utils, enums, signals, fields
from nimbus.libs.template import render_to_file, render_to_string

OS = ( (os,os) for os in enums.operating_systems)


class UnableToGetFile(Exception):
    # TODO: TRATAR
    pass


class ComputerAlreadyActive(Exception):
    # TODO: TRATAR
    pass


class ComputerGroup(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name = u"Grupo de computadores"


class CryptoInfo(models.Model):
    key = models.CharField( max_length=2048, blank=False, null=False)
    certificate = models.CharField( max_length=2048, blank=False, null=False)
    pem = models.CharField( max_length=4096, blank=False, null=False)


class ComputerNewClass(BaseModel):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False,
                            validators=[fields.check_model_name])

class Computer(BaseModel):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False,
                            validators=[fields.check_model_name])
    address = models.IPAddressField(blank=False, null=False, unique=True)
    operation_system = models.CharField(max_length=255, blank=False, null=False,
                                        choices=OS )
    description = models.TextField(max_length=1024, blank=True)
    password = models.CharField(max_length=255, blank=False, null=False, 
                                editable=False, default=utils.random_password)
    groups = models.ManyToManyField(ComputerGroup, related_name="computers", 
                                    blank=True, null=True)
    active = models.BooleanField(editable=False)
    crypto_info = models.ForeignKey(CryptoInfo, null=False, blank=False, 
                                    unique=True, editable=False)



    class Meta:
        verbose_name = u"Computador"


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


    def _procedure_names(self):
        return [ p.bacula_name for p in self.procedure_set.all() ]


    def successful_jobs(self):
        return Job.objects.filter(jobstatus__in=('T','W'),
                                  name__in=self._procedure_names(),
                                  client__name=self.bacula_name)\
                                        .order_by('-endtime').distinct()[:15]

    def unsuccessful_jobs(self):
        return Job.objects.filter(jobstatus__in=('E','e','f','I'), 
                                  client__name=self.bacula_name)\
                                        .order_by('-endtime').distinct()[:15]

    def running_jobs(self):
        status = ('R','p','j','c','d','s','M','m','s','F','B')
        return Job.objects.filter(jobstatus__in=status, 
                                  name__in=self._procedure_names(),
                                  client__name=self.bacula_name)\
                                        .order_by('-starttime').distinct()[:5]

    def last_jobs(self):
        return Job.objects.filter(client__name=self.bacula_name,
                                  name__in=self._procedure_names())\
                                        .order_by('-endtime').distinct()[:15]

    @property
    def all_my_jobs(self):
        return Job.objects.filter(client__name=self.bacula_name,
                                  name__in=self._procedure_names())\
                                        .order_by('-endtime').distinct()
    

    def error_jobs(self):
        return Job.objects.filter(jobstatus__in=('e','E','f'),
                                  name__in=self._procedure_names(),
                                     client__name=self.bacula_name)\
                                            .order_by('-endtime').distinct()[:5]

    def configure(self):
        nimbuscomputer = Computer.objects.get(id=1)
        url = "http://%s:%d" % (self.address, settings.NIMBUS_CLIENT_PORT)
        proxy = xmlrpclib.ServerProxy(url)
        proxy.save_keys(self.crypto_info.pem,
                        nimbuscomputer.crypto_info.certificate)
        config = Config.get_instance()
        fdconfig = render_to_string("bacula-fd",
                                    director_name=config.director_name,
                                    password=self.password,
                                    name=self.name,
                                    os=self.operation_system)
        proxy.save_config(unicode(fdconfig))
        proxy.restart_bacula()

    def activate(self):
        if self.active:
            raise ComputerAlreadyActive("O computador já está ativo")
        self.configure() 
        self.active = True
        self.save()

    def get_file_tree(self, path):
        url = "http://%s:%d" % (self.address, settings.NIMBUS_CLIENT_PORT)
        proxy = xmlrpclib.ServerProxy(url)
        if self.operation_system == "windows" and path == "/":
            files = proxy.get_available_drives()
            files = [ fname[:-1] + '/' for fname in files ]
        else:
            files = proxy.list_dir(path)
        files.sort()
        return files

    def deactivate(self):
        self.active = False
        self.save()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.address)


def update_computer_file(computer):
    """Computer update file"""
    if computer.active:
        name = computer.bacula_name
        filename = path.join( settings.NIMBUS_COMPUTERS_DIR, name)
        render_to_file(filename, "client", name=name, ip=computer.address,
                       password=computer.password)

def remove_computer_file(computer):
    """Computer remove file"""
    if computer.active:
        filename = path.join(settings.NIMBUS_COMPUTERS_DIR, 
                             computer.bacula_name)
        utils.remove_or_leave(filename)

def generate_keys(computer):
    try:
        computer.crypto_info
    except CryptoInfo.DoesNotExist, error:
        key, cert, pem = keymanager.generate_all_keys(settings.NIMBUS_SSLCONFIG)
        info = CryptoInfo.objects.create(key=key, certificate=cert, pem=pem)
        computer.crypto_info = info

signals.connect_on(generate_keys, Computer, pre_save)
signals.connect_on(update_computer_file, Computer, post_save)
signals.connect_on(remove_computer_file, Computer, post_delete)
