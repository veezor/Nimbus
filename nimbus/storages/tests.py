#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
from datetime import datetime

from django.conf import settings
from django.test import TestCase

from nimbus.storages import models, admin
from nimbus.config.models import Config

class StorageAdminTest(TestCase):

    def test_storage(self):
        self.assertTrue( models.Storage in admin.admin.site._registry)

    def test_device(self):
        self.assertTrue( models.Device in admin.admin.site._registry)

    def test_storage_graphic_data(self):
        self.assertTrue( models.StorageGraphicsData in admin.admin.site._registry)




class StorageGraphicsDataModelTest(TestCase):
    
    def test_unicode(self):
        date = datetime(2012, 03, 12)
        data = models.StorageGraphicsData(total=100,
                                          used=50,
                                          timestamp=date)
        self.assertEqual(unicode(data), 
                         "00:00:00 12/03/2012 - 50 de 100 (50.00%)")




EXPECTED_BACULA_SD_FILE="""\
Storage {
    Name = %(name)s
    WorkingDirectory = "/var/bacula/working"
    Maximum Concurrent Jobs = 100 
    SDPort = 9103
    PidDirectory = "/var/run"
    Client Connect Wait = 30 seconds
    }

Director {
	Name = director_name
	Password = "password"
}

Messages {
	Name = Standard
	Director = director_name = all
}

@|"sh -c 'for f in %(root)s/var/nimbus/custom/devices/* ; do echo @${f} ; done'"

"""



class StorageModelTest(TestCase):


    def setUp(self):
        self.maxDiff = None
        self.storage = models.Storage(name="test", 
                                      address="192.168.0.1",
                                      password="password")


    def test_is_local(self):
        with mock.patch("nimbus.storages.models.get_nimbus_address")\
                as mock_nimbus_address:
            mock_nimbus_address.return_value = "192.168.0.2"
            self.assertFalse(self.storage.is_local)
            mock_nimbus_address.return_value = "192.168.0.1"
            self.assertTrue(self.storage.is_local)


    def test_unicode(self):
        self.assertEqual(unicode(self.storage), 
                        "(test:192.168.0.1)")


    def test_computers(self):
        """ TODO """
        pass


    def test_create_archive(self):
        self.assertEqual(self.storage.devices.count(), 0)
        self.storage.save()
        device = self.storage.devices.all()[0]
        self.assertEqual(device.name, "device default")
        self.assertEqual(device.archive, u"/bacula/")
        self.assertEqual(self.storage.devices.count(), 1)


    def test_update_storage_file(self):
        template = EXPECTED_BACULA_SD_FILE

        with mock.patch("nimbus.storages.models.get_nimbus_address")\
                as mock_nimbus_address:
            mock_nimbus_address.return_value = "192.168.0.1"
            self.storage.active = True
            self.storage.save()
            config = Config(name="config test",
                            director_name="director_name",
                            director_password="director_password",
                            director_address="192.168.0.1")
            config.save()

            models.update_storage_file(self.storage)
            template = template % { "root" : settings.ROOT_PATH ,
                                    "name" : self.storage.bacula_name}

            with file(settings.BACULASD_CONF) as f_obj:
                content = f_obj.read()
                self.assertMultiLineEqual(content, template)



    def test_update_storage_devices(self):
        with mock.patch("nimbus.storages.models.update_device_file")\
                as m_update:
            self.storage.save()
            models.update_storage_devices(self.storage)
            for device in self.storage.devices.all():
                m_update.assert_called_with(device)


    def test_baculasd_restart(self):
        with mock.patch("pybacula.configcheck.check_baculasd") as mock_check:
            with mock.patch("xmlrpclib.ServerProxy") as mock_cls_proxy:
                mock_proxy = mock_cls_proxy.return_value
                models.restart_bacula_storage(self.storage)
                mock_check.assert_called_with(settings.BACULASD_CONF)
                mock_cls_proxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
                mock_proxy.storage_restart.assert_called_with()




EXPECTED_STORAGE_CONF_FILE="""\

Storage {
	Name = %(storage)s
	Media Type = File
	Address = 192.168.0.1
	Device = %(device)s
	Password = "password"
	SDPort = 9103
}

"""

EXPECTED_DEVICE_FILE="""\
Device {
	Name = %(device)s
	LabelMedia = yes
	AlwaysOpen = no
	Random Access = yes
	Archive Device = /nimbus
	Media Type = File
	RemovableMedia = no
	AutomaticMount = yes
}
"""

class DeviceModelTest(TestCase):

    def setUp(self):
        self.storage = models.Storage(name="test", 
                                      address="192.168.0.1",
                                      active=True,
                                      password="password")
        self.device = models.Device(name="test", 
                                    archive="/nimbus",
                                    storage=self.storage)
        self.maxDiff = None

    def test_is_local(self):
        with mock.patch("nimbus.storages.models.get_nimbus_address")\
                as mock_nimbus_address:
            mock_nimbus_address.return_value = "192.168.0.2"
            self.assertFalse(self.device.is_local)
            mock_nimbus_address.return_value = "192.168.0.1"
            self.assertTrue(self.device.is_local)


    def test_unicode(self):
        self.assertEqual(unicode(self.device), 
                        "test in /nimbus")


    def _save(self):
        self.storage.save()
        self.device.storage = self.storage

        models.Device.objects.all().delete() 
        # FIX: storage.save creates a device

        self.device.save()


    def _set_filenames(self):
        name = self.device.bacula_name
        storagename = self.storage.bacula_name
        self.filename = os.path.join(settings.NIMBUS_DEVICES_DIR, 
                                name)
        self.storagefile = os.path.join( settings.NIMBUS_STORAGES_DIR, 
                                    storagename)



    def test_update_device_file(self):
        self._save()
        self._set_filenames()

        
        models.update_device_file(self.device)

        template_device = EXPECTED_DEVICE_FILE \
                % { "device" : self.device.bacula_name }

        template_storage = EXPECTED_STORAGE_CONF_FILE \
                % { "device" : self.device.bacula_name,
                    "storage" : self.storage.bacula_name}

        with file(self.filename) as f_obj:
            content = f_obj.read()
            self.assertMultiLineEqual(content, template_device)

        with file(self.storagefile) as f_obj:
            content = f_obj.read()
            self.assertMultiLineEqual(content, template_storage)

    
    def test_remove_device_file(self):
        self._save()
        self._set_filenames()
        self.assertTrue(os.path.exists(self.filename))
        self.assertTrue(os.path.exists(self.storagefile))
        self.device.delete()
        self.assertFalse(os.path.exists(self.filename))
        self.assertFalse(os.path.exists(self.storagefile))



