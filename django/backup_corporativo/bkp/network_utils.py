#!/usr/bin/python
# -*- coding: utf-8 -*-

import netifaces

class NetworkInfo:
    # Classmethods
	def interfaces(cls):
		valid_interfaces = []
		# TODO: melhorar forma de identificar interfaces válidas.
		for iface in netifaces.interfaces():
			if iface != "lo": # Retirar loopback da lista
				valid_interfaces.append(iface)
		return valid_interfaces
	interfaces = classmethod(interfaces)

	def ip_address(cls, iface_name):
		try:
			return netifaces.ifaddresses(iface_name)[2][0]["addr"]
		except KeyError:
			return ''
	ip_address = classmethod(ip_address)

	def broadcast_address(cls, iface_name):
		try:
			return netifaces.ifaddresses(iface_name)[2][0]["broadcast"]
		except KeyError:
			return ''
	broadcast_address = classmethod(broadcast_address)

	def netmask(cls, iface_name):
		try:
			return netifaces.ifaddresses(iface_name)[2][0]["netmask"]
		except KeyError:
			return ''
	netmask = classmethod(netmask)

	def mac_address(cls, iface_name):
		try:
			return netifaces.ifaddresses(iface_name)[17][0]["addr"]
		except KeyError:
			return ''
	mac_address = classmethod(mac_address)
	
	def mac_choices(cls):
		interfaces = cls.interfaces()
		choices = []
		for iface in interfaces:
			mac_address = cls.mac_address(iface)
			if mac_address:
				choices.append((mac_address,mac_address))
		return choices
	mac_choices = classmethod(mac_choices)
	
	def main_mac_address(cls):
		iface = cls.interfaces()[0]
		macaddress = cls.mac_address(iface)
		return macaddress and macaddress or 'MAC'
	main_mac_address = classmethod(main_mac_address)
