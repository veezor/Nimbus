#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import mock
import networkutils

from django.test import TestCase
from django.conf import settings
from django.db.models.signals import post_save

from nimbus.network import models, admin
from nimbus.config.models import Config
from nimbus.storages.models import Storage
from nimbus.storages.models import Computer

class NetworkAdminRegistry(TestCase):

    def test_network_interface(self):
        self.assertTrue( models.NetworkInterface in admin.admin.site._registry)


class NetworkModelTest(TestCase):

    def setUp(self):
        self.patch = mock.patch("networkutils.get_interfaces")
        self.mock_interfaces = self.patch.start()
        self.mock_interface = mock.Mock()
        self.mock_interface.addr = "192.168.0.100"
        self.mock_interface.netmask = "255.255.255.0"
        self.mock_interfaces.return_value = [self.mock_interface]

        self.interface = models.NetworkInterface()
 
        self.signals = {}
        self.signal_names = [ "update_director_address",
                              "update_networks_file",
                              "update_storage_address",
                              "update_nimbus_client_address" ]

 

    def tearDown(self):
        self.patch.stop()
        self._enable_signals()


    def _enable_signals(self):
        for signal in self.signals.values():
            post_save.connect( signal,
                               sender=models.NetworkInterface,
                               weak=True )
 
    def _disable_signals(self):
       for name in self.signal_names:
            for (s_id, signal) in post_save.receivers:
                if signal.__name__ == name:
                    self.signals[name] = signal
                    post_save.disconnect(signal, 
                                         sender=models.NetworkInterface,
                                         weak=True)

    def test_init(self):
        interface = models.NetworkInterface()
        self.assertEqual(interface.address, "192.168.0.100")
        self.assertEqual(interface.netmask, "255.255.255.0")
        self.assertEqual(interface.gateway, interface.default_gateway)
        self.assertEqual(interface.dns1, interface.default_gateway)

    def test_default_gateway(self):
        self.assertEqual(self.interface.default_gateway, 
                         "192.168.0.1")

    def test_broadcast(self):
        self.assertEqual(self.interface.broadcast, 
                         "192.168.0.255")

    def test_network(self):
        self.assertEqual(self.interface.network, 
                         "192.168.0.0")

    def test_unicode(self):
        self.assertEqual(unicode(self.interface),
                         "192.168.0.100/255.255.255.0")

    def test_get_raw_address(self):
        self.assertEqual(models.get_raw_network_interface_address(),
                         "192.168.0.100")

    def test_get_nimbus_address(self):
        self._disable_signals()
        self.assertEqual(models.get_nimbus_address(),
                         "192.168.0.100")

        config =  Config(name="test",
                         director_name="director_name_test",
                         director_address="192.168.0.101",
                         director_password="Bazinga!")
        config.save()


        self.assertEqual(models.get_nimbus_address(),
                         "192.168.0.101")


    def test_update_director_address(self):
        config = Config.get_instance()
        self.assertEqual(config.director_address,
                            "192.168.0.100")
        self.interface.address = "192.168.0.102"
        models.update_director_address(self.interface)
        config = Config.get_instance()
        self.assertEqual(config.director_address,
                            "192.168.0.102")


    def test_update_storage_address(self):
        storage = Storage(name="test", address="192.168.0.100")
        storage.save()
        self.assertEqual(storage.address,
                         "192.168.0.100")
        self.interface.address = "192.168.0.102"
        models.update_storage_address(self.interface)
        storage = Storage.objects.get(id=1)
        self.assertEqual(storage.address,
                         "192.168.0.102")


    def test_update_cliente_address(self):
        computer = Computer(name="test", 
                            address="192.168.0.100",
                            active=True,
                            operation_system="unix")
        computer.save()
        self.assertEqual(computer.address,
                         "192.168.0.100")
        self.interface.address = "192.168.0.102"
        models.update_nimbus_client_address(self.interface)
        computer = Computer.objects.get(id=1)
        self.assertEqual(computer.address,
                         "192.168.0.102")


    def test_update_networks_file(self):
        with mock.patch("nimbus.network.models.ServerProxy") as mock_proxy_cls:
            mock_proxy = mock_proxy_cls.return_value
            models.update_networks_file(self.interface)
            mock_proxy_cls.assert_called_with(settings.NIMBUS_MANAGER_URL)
            mock_proxy.generate_interfaces("eth0",
                                           "192.168.0.100",
                                           "255.255.255.0",
                                           "static",
                                           "192.168.0.255",
                                           "192.168.0.0",
                                           "192.168.0.1")
            mock_proxy.generate_dns.assert_called_with("192.168.0.1",
                                                       "192.168.0.1")
            mock_proxy.network_restart.assert_called_with()


    def test_signal_connect(self):
        names = ["nimbus.computers.models.Computer",
                 "nimbus.storages.models.Storage",
                 "nimbus.config.models.Config"]

        mocks = {}
        for name in names:
            patch = mock.patch(name)
            mock_signal = patch.start()
            s_name = name.split('.')[-1]
            mocks[s_name] = { "patch" : patch, "mock" : mock_signal }

        self.interface.save()

        for name in mocks:
            mocks[name]["patch"].stop()

        mocks["Computer"]["mock"].objects.get.assert_called_with(id=1)
        mocks["Storage"]["mock"].objects.get.assert_called_with(id=1)
        mocks["Config"]["mock"].get_instance.assert_called_with()


