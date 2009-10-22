#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import netifaces
from netifaces import AF_INET, AF_LINK, AF_INET6

class InterfaceNotFound(Exception):
    pass

class Interface(object):

    def __init__(self, name):
        self.name = name
        data = netifaces.ifaddresses(name)
        try:
            inet =  data[AF_INET][0]
            link = data[AF_LINK][0]
            self.addr = inet['addr']
            self.broadcast = inet['broadcast']
            self.netmask = inet['netmask']
            self.mac = link['addr']
        except KeyError:
            raise InterfaceNotFound()

    def __repr__(self):
        return self.__class__.__name__ + "(%s)" % (self.name)



def get_interface(name):
    try:
        iface = Interface(name)
    except KeyError:
        raise InterfaceNotFound()
    return iface


def get_interfaces():
    interfaces = []
    for name in netifaces.interfaces():
        try:
            interface = Interface(name)
            interfaces.append(interface)
        except InterfaceNotFound:
            pass
    return interfaces
