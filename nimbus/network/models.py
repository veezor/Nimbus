#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from xmlrpclib import ServerProxy
from IPy import IP
import time
import networkutils

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core.exceptions import ValidationError

from nimbus.shared import signals
from nimbus.libs import systemprocesses, bacula
from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.config.models import Config
from nimbus.storages.models import Storage
from nimbus.computers.models import Computer


class NetworkInterface(BaseModel):
    address = models.IPAddressField(null=False)
    netmask = models.IPAddressField(null=False)
    gateway = models.IPAddressField(null=False)
    dns1 = models.IPAddressField(null=False)
    dns2 = models.IPAddressField(blank=True,null=True)

    def __init__(self, *args, **kwargs):
        super(NetworkInterface, self).__init__(*args, **kwargs)
        if not self.id:
            raw_iface = networkutils.get_interfaces()[0]
            self.address = raw_iface.addr
            self.netmask = raw_iface.netmask
            self.gateway = self.default_gateway
            self.dns1 = self.default_gateway

    def clean(self):
        raw_iface = networkutils.get_interfaces()[0]
        if self.address == raw_iface.addr:
            return
        returncode, stdout = networkutils.ping(self.address, packets=1)
        if not returncode:
            raise ValidationError(u'Erro, existe outra máquina com o mesmo IP na rede.')

    def __unicode__(self):
        return u"%s/%s" % (self.address, self.netmask)

    def _get_net_object(self):
        net = IP(self.address).make_net(self.netmask)
        return net

    @property
    def broadcast(self):
        net = self._get_net_object()
        return str(net.broadcast())

    @property
    def network(self):
        net = self._get_net_object()
        return str(net.net())

    @property
    def default_gateway(self):
        net = self._get_net_object()
        return str(net[1])


def update_networks_file(interface):
    def callable(interface):
        try:
            time.sleep(10) # for redirect page
            server = ServerProxy(settings.NIMBUS_MANAGER_URL)
            server.generate_interfaces("eth0", 
                                       interface.address, 
                                       interface.netmask, 
                                       "static",
                                       interface.broadcast, 
                                       interface.network, 
                                       interface.gateway)
            server.generate_dns(interface.dns1, 
                                 interface.dns2)
            server.network_restart()
        except Exception, error:
            logger = logging.getLogger(__name__)
            logger.exception("Conexao com nimbus-manager falhou")
    if not bacula.bacula_is_locked():
        systemprocesses.norm_priority_job("Generate network conf files and restart networking", 
                                         callable, interface)


def update_director_address(interface):
    config = Config.get_instance()
    config.director_address = interface.address
    config.save(system_permission=True)
    logger = logging.getLogger(__name__)
    logger.info("Atualizando ip do director")

def update_storage_address(interface):
    storage = Storage.objects.get(id=1) # storage default
    storage.address = interface.address
    storage.save(system_permission=True)
    logger = logging.getLogger(__name__)
    logger.info("Atualizando ip do storage")

def update_nimbus_client_address(interface):
    computer = Computer.objects.get(id=1) # storage default
    computer.address = interface.address
    computer.save(system_permission=True)
    logger = logging.getLogger(__name__)
    logger.info("Atualizando ip do client nimbus")

def get_nimbus_address():
    config = Config.get_instance()
    if not config.director_address:
        return get_raw_network_interface_address()
    return config.director_address

def get_raw_network_interface_address():
    raw_iface = networkutils.get_interfaces()[0]
    return raw_iface.addr

signals.connect_on(update_networks_file, NetworkInterface, post_save)
signals.connect_on(update_director_address, NetworkInterface, post_save)
signals.connect_on(update_storage_address, NetworkInterface, post_save)
signals.connect_on(update_nimbus_client_address, NetworkInterface, post_save)