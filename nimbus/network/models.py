
import iplib
import networkutils

from django.db import models
from nimbus.base.models import UUIDSingletonModel as BaseModel

# Create your models here.

class NetworkInterface(BaseModel):
    address = models.IPAddressField(null=False)
    netmask = models.IPAddressField(null=False)
    gateway = models.IPAddressField(null=False)
    dns1 = models.IPAddressField(null=False)
    dns2 = models.IPAddressField(blank=True)


    @property
    def broadcast(self):
        mask = iplib.IPv4NetMask(self.netmask)
        ip =  iplib.IPv4Address(self.address)
        cidr = iplib.CIDR(ip, mask)
        return str(cidr.get_broadcast_ip())


    @property
    def network(self):
        mask = iplib.IPv4NetMask(self.netmask)
        ip =  iplib.IPv4Address(self.address)
        cidr = iplib.CIDR(ip, mask)
        return str(cidr.get_network_ip())


    @classmethod
    def new(cls):
        interface = cls.get_instance()

        raw_iface = networkutils.get_interfaces()[0]
        interface.address = raw_iface.addr
        interface.netmask = raw_iface.netmask

        interface.save()
        return interface




