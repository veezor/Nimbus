import netifaces

class NetworkInfo:
    # Classmethods
    def interfaces(cls):
            return netifaces.interfaces()
    interfaces = classmethod(interfaces)

    def ip_address(cls):
            return netifaces.ifaddresses(cls.stub_interface_name())[2][0]["addr"]
    ip_address = classmethod(ip_address)

    def broadcast_address(cls):
            return netifaces.ifaddresses(cls.stub_interface_name())[2][0]["broadcast"]
    broadcast_address = classmethod(broadcast_address)

    def netmask(cls):
            return netifaces.ifaddresses(cls.stub_interface_name())[2][0]["netmask"]
    netmask = classmethod(netmask)

    def mac_address(cls):
            return netifaces.ifaddresses(cls.stub_interface_name())[17][0]["addr"]
    mac_address = classmethod(mac_address)

    def stub_interface_name(cls):
		return 'eth2'
	stub_interface_name = classmethod(stub_interface_name)
