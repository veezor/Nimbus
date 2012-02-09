#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import networkutils





class NetworkTest(unittest.TestCase):

    def test_inexistent_interface(self):
        self.assertRaises(networkutils.InterfaceNotFound,
                          networkutils.get_interface,
                          "xxx")

    def test_get_interface(self):
        interface = networkutils.get_interface("lo")
        self.assertEquals(interface.addr, "127.0.0.1")
        self.assertEquals(interface.netmask, "255.0.0.0")
        self.assertEquals(interface.mac, "00:00:00:00:00:00")


    def test_get_interfaces(self):
        ifaces = networkutils.get_interfaces()
        self.assertNotEqual(0, len(ifaces))

    def test_contains_lo(self):
        ifaces = networkutils.get_interfaces()
        iface_names = [ i.name for i in ifaces ]
        self.assertTrue( "lo" in iface_names )

    def test_resolve_name(self):
        address = networkutils.resolve_name("localhost")
        self.assertEquals(address, "127.0.0.1")

    def test_resolve_address(self):
        name = networkutils.resolve_addr("127.0.0.1")
        self.assertEquals(name, "localhost")

    def test_ping(self):
        code, stdout = networkutils.ping("127.0.0.1")
        self.assertEquals(code, 0)

    def test_traceroute(self):
        code, stdout = networkutils.traceroute("127.0.0.1")
        self.assertEquals(code, 0)

    def test_fail_ping(self):
        code, stdout = networkutils.ping("169.254.1.2")
        self.assertNotEquals(code, 0)

    def test_fail_traceroute(self):
        code, stdout = networkutils.traceroute("169.254.1.2")
        self.assertNotEquals(code, 0)

    def test_ping_google(self):
        code, stdout = networkutils.ping("www.google.com")
        self.assertEquals(code, 0)

    def test_traceroute_google(self):
        code, stdout = networkutils.traceroute("www.google.com")
        self.assertEquals(code, 0)




if __name__ == "__main__":
    unittest.main()

