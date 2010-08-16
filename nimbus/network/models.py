#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import logging
from xmlrpclib import ServerProxy

import iplib
import networkutils

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings


from nimbus.shared import signals
from nimbus.shared.middlewares import ThreadPool
from nimbus.base.models import UUIDSingletonModel as BaseModel

# Create your models here.

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




    def __unicode__(self):
        return u"%s/%s" % (self.address, self.netmask)


    def _get_cidr(self):
        mask = iplib.IPv4NetMask(self.netmask)
        ip =  iplib.IPv4Address(self.address)
        cidr = iplib.CIDR(ip, mask)
        return cidr



    @property
    def broadcast(self):
        cidr = self._get_cidr()
        return str(cidr.get_broadcast_ip())


    @property
    def network(self):
        cidr = self._get_cidr()
        return str(cidr.get_network_ip())

    @property
    def default_gateway(self):
        cidr = self._get_cidr()
        return str(cidr.get_first_ip())






def update_networks_file(interface):

    def callable(interface):
        try:
            server = ServerProxy(settings.NIMBUS_MANAGER_URL)

            server.generate_interfaces( "eth0", 
                    interface.address, 
                    interface.netmask, 
                    "static",
                    interface.broadcast, 
                    interface.network, 
                    interface.gateway)

            server.generate_dns( interface.dns1, 
                                 interface.dns2)
        except Exception, error:
            logger = logging.getLogger(__name__)
            logger.exception("Conexao com nimbus-manager falhou")


    Pool = ThreadPool.get_instance()
    Pool.add_job( callable, (interface,), {} )


signals.connect_on( update_networks_file, NetworkInterface, post_save )
