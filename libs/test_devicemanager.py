#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
import unittest
import devicemanager


REAL_DEVICE = False


class StorageTest(unittest.TestCase):


    def setUp(self):
        self.device = devicemanager.StorageDeviceManager('test')
        self.patch_readlink = mock.patch('os.readlink')
        self.mock_readlink = self.patch_readlink.start()
        self.mock_readlink.return_value = '/dev/test'

        self.patch_disk_labels = mock.patch('devicemanager.list_disk_labels')
        self.mock_disk_labels = self.patch_disk_labels.start()
        self.mock_disk_labels.return_value = ['test_label']

        self.patch_check_call = mock.patch('devicemanager.check_call')
        self.mock_check_call = self.patch_check_call.start()
        self.mock_check_call.return_value = 0

        self.patch_statvfs = mock.patch('os.statvfs')
        self.mock_statvfs = self.patch_statvfs.start()
        stat = self.mock_statvfs.return_value
        stat.f_bsize = 10
        stat.f_blocks = 6
        stat.f_bfree = 3



    def tearDown(self):
        self.patch_readlink.stop()
        self.patch_disk_labels.stop()
        self.patch_check_call.stop()
        self.patch_statvfs.stop()

    def test_list_devices(self):
        devices = devicemanager.list_devices()
        self.assertEqual(len(devices), 1)
        device = devices[0]
        self.assertTrue( isinstance(device, devicemanager.StorageDeviceManager))
        self.assertEqual( device.labelname, 'test_label')


    def test_repr(self):
        self.assertEqual(repr(self.device), 'StorageDeviceManager(test)')

    def test_mountpoint(self):
        self.assertEqual(self.device.mountpoint, '/media/test')

    def test_device(self):
        self.assertEqual(self.device.device, '/dev/test')


    def test_mounted_ok(self):
        with mock.patch('__builtin__.file') as mmock:
            mmock.return_value.read.return_value = '/dev/test'
            self.assertTrue( self.device.mounted )

    def test_mounted_fail(self):
        with mock.patch('__builtin__.file') as mmock:
            mmock.return_value.read.return_value = '/dev/null'
            self.assertFalse( self.device.mounted )


    def test_mount(self):
        self.device.mount()


    def test_umount(self):
        with mock.patch('__builtin__.file') as mmock2:
            mmock2.return_value.read.return_value = '/dev/test'
            self.device.umount()


    def test_storage_info(self):
        with mock.patch('__builtin__.file') as mmock2:
            mmock2.return_value.read.return_value = '/dev/test'
            total,used,free = self.device._storage_info()
            self.assertEqual(total, 60)
            self.assertEqual(used, 30)
            self.assertEqual(free, 30)
            self.mock_statvfs.assert_called_with(self.device.mountpoint)

    def test_available_size(self):
        with mock.patch('__builtin__.file') as mmock2:
            mmock2.return_value.read.return_value = '/dev/test'
            self.assertEqual(self.device.available_size, 30)


    def test_size(self):
        with mock.patch('__builtin__.file') as mmock2:
            mmock2.return_value.read.return_value = '/dev/test'
            self.assertEqual(self.device.size, 60)


    def test_used_size(self):
        with mock.patch('__builtin__.file') as mmock2:
            mmock2.return_value.read.return_value = '/dev/test'
            self.assertEqual(self.device.used_size, 30)




if REAL_DEVICE: #tests with a real device. Check labelname of device
    class RealStorageDeviceTest(unittest.TestCase):

        def setUp(self):
            self.label = 'RODRIGO' #real device label
            self.device = devicemanager.StorageDeviceManager(self.label)

        def test_mount(self):
            self.device.mount()
            self.assertTrue(self.device.mounted)
            with file( os.path.join(self.device.mountpoint, "test-mount"), "w" ) as f:
                f.write("test")


        def test_umount(self):
            self.device.mount()
            self.assertTrue(self.device.mounted)
            self.device.umount()
            self.assertFalse(self.device.mounted)
            self.assertRaises(IOError, file, os.path.join(self.device.mountpoint, "test-mount"), "w")


        def test_list_disk_labels(self):
            self.assertTrue( self.label in devicemanager.list_disk_labels())




if __name__ == "__main__":
    unittest.main()
