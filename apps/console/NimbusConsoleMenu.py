#! /usr/bin/env python2.4
# -*- coding: iso-8859-1 -*-
import os
from SOAPpy import SOAPProxy

server = SOAPProxy("http://127.0.0.1:8888")

def ConsoleMenu(str_mn,title='Nimbus Config System'):
	os.system("clear")
	print title
	if str_mn["tp"] == "list":
		for opt in str_mn["menu"]:
			print opt
	elif str_mn["tp"] == "input":
		exec str_mn["menu"]
	sel = raw_input("nimbus:~#")
	return str_mn["optout"][sel]
	
def netinfo():
	lstnet = server.get_interface_set("eth0")
	outlst = []
	outlst.append("IP: %s" % lstnet[0])
	outlst.append("Broadcast: %s" % lstnet[1])
	outlst.append("Netmask: %s" % lstnet[2])
	outlst.append("1 - Back Menu / 2 - Main Menu")
	return outlst

def netgenerate():
    net_confirm = "N"
    while net_confirm == "N":
        net_ip = raw_input("IP:")
        net_broad = raw_input("Broadcast:")
        net_mask = raw_input("Netmask:")
        net_confirm = raw_input("Confirm: Y/n :~#")
        if net_confirm == "Y":
            server.generate_interfaces("eth0", net_ip, net_mask, type="static", broad=net_broad)
            break
    print "1 - Back Menu / 2 - Main Menu"

menu_principal = ["1 - Network Settings","2 - Nimbus Backup Server Product Activation"]
str_principal = {"id":1,"tp":"list","menu":menu_principal,"optout":{"1":2,"2":3}}
menu_netset = ["1 - View Network Settings","2 - Configure Network"]
str_netset = {"id":2,"tp":"list","menu":menu_netset,"optout":{"1":4,"2":5}}
str_vnetset = {"id":4,"tp":"list","menu":netinfo(),"optout":{"1":2,"2":1}}
str_netgen = {"id":5,"tp":"input","menu":"netgenerate()","optout":{"1":2,"2":1}}


console = {1:str_principal,2:str_netset,4:str_vnetset,5:str_netgen}
opt = 1
while True:
	str = console[opt]
	opt = ConsoleMenu(str)
