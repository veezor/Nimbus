import os
import netifaces

os.system("clear")
print "Nimbus Config System"
print "1 - Network Settings"
print "2 - Activate Nimbus"
opt = raw_input("nimbus:~#")

os.system("clear")
if opt == "1":
	print "Nimbus Config System"
	print "1 - View Network Settings"
	print "2 - Configure Network"
	opt = raw_input("#>")
os.system("clear")
if opt == "1":
	print "Nimbus Config System"
	for iface in netifaces.interfaces():
		if iface == "eth0":
			list = netifaces.ifaddresses(iface)
			print "Interface: %s" %  iface 
			print "IP: %s" % list[2][0]['addr']
			print "Broadcast: %s" % list[2][0]['broadcast']
			print "Netmask: %s" % list[2][0]['netmask']
			print "MAC Address: %s" % list[17][0]['addr']
