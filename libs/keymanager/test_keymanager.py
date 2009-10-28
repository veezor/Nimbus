#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import truecrypt
import keymanager
from mock import Mock
import os
import pdb
import sys


class KeyManagerMockTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.password = "1234"
        self.drive = "/tmp/strongbox.crypto"
        self.mountpoint = "/tmp/strongbox"
        self.keymanager = keymanager.KeyManager( password = self.password,
                                                 drive = self.drive,
                                                 mountpoint = self.mountpoint )
        self.mock = Mock()
        self.mock.return_value = Mock()
        self.mock.return_value.returncode = 0
        self.getpopen = truecrypt.TrueCrypt._get_popen
        truecrypt.TrueCrypt._get_popen = self.mock # MonkeyPatch
        


    def test_create(self):

        km = keymanager.KeyManager( password = self.password,
                                                 drive = self.drive,
                                                 mountpoint = self.mountpoint )
        self.assertEqual( self.password, km.password )
        self.assertEqual( self.drive, km.drive )
        self.assertEqual( self.mountpoint, km.mountpoint )
        self.assertFalse( km.mounted )


    def test_set_password(self):
        password = "4567"
        self.keymanager.set_password(password)
        self.assertEqual( self.keymanager.password, password )
        self.keymanager.set_password(self.password)

    def test_mount_drive(self):
        r = self.keymanager.mount_drive()
        self.assertTrue( r )
        self.assertTrue( self.keymanager.mounted )

    def test_create_drive(self):
        r = self.keymanager.create_drive()
        self.assertTrue( r )

    def test_umount_drive(self):
        r = self.keymanager.umount_drive()
        self.assertTrue( r )
        self.assertFalse( self.keymanager.mounted )

    def test_force_umount_drive(self):
        r = self.keymanager.force_umount_drive()
        self.assertTrue( r )
        self.assertFalse( self.keymanager.mounted )

    def tearDown(self):
        truecrypt.TrueCrypt._get_popen = self.getpopen # remove Mock





#class TrueCryptTest(unittest.TestCase):
#
#    def setUp(self):
#        unittest.TestCase.setUp(self)
#        reload(truecrypt) # remove mock
#        self.truecrypt = truecrypt.TrueCrypt()
#        self.assertFalse( isinstance(truecrypt.TrueCrypt._get_popen, Mock) )
#        self.filedrive = "/tmp/drive.crypto"
#        self.mountpoint = "/tmp/drivetest"
#        self.password = '1234'
#        self.fileback = '/tmp/drive.crypto.back'
#
#    def test_create_drive(self):
#        r = self.truecrypt.create_drive(self.password, self.filedrive)
#        self.assertTrue(r)
#
#
#    def mount_drive(self):
#
#        try:
#            os.mkdir(self.mountpoint)
#        except OSError:
#            pass #silent file exists
#
#        r = self.truecrypt.mount_drive(self.password, self.filedrive, self.mountpoint)
#        self.assertTrue(r)
#
#
#    def test_umount_drive(self):
#        self.mount_drive()
#        r = self.truecrypt.umount_drive( self.filedrive )
#        self.assertTrue(r)
#
#    def test_umountf_drive(self):
#        self.mount_drive()
#        r = self.truecrypt.umountf_drive( self.filedrive )
#        self.assertTrue(r)
#
#    def test_make_backup(self):
#        r = self.truecrypt.make_backup(self.password, self.fileback, self.filedrive)
#        self.assertTrue(r)
#
#
#    def test_restore_backup(self):
#        self.test_make_backup()
#        r = self.truecrypt.restore_backup(self.password, self.fileback, self.filedrive)
#        self.assertTrue(r)
#


if __name__ == "__main__":
    unittest.main()

