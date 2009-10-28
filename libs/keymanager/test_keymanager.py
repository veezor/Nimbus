#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import truecrypt
import keymanager
import os
import pdb
import sys


class KeyManagerTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.password = "1234"
        self.drive = "/tmp/strongbox.crypto"
        self.mountpoint = "/tmp/strongbox"
        self.keymanager = keymanager.KeyManager( password = self.password,
                                                 drive = self.drive,
                                                 mountpoint = self.mountpoint )
        


    def test_1_create(self):

        km = keymanager.KeyManager( password = self.password,
                                                 drive = self.drive,
                                                 mountpoint = self.mountpoint )
        self.assertEqual( self.password, km.password )
        self.assertEqual( self.drive, km.drive )
        self.assertEqual( self.mountpoint, km.mountpoint )
        self.assertFalse( km.mounted )


    def test_2_set_password(self):
        password = "4567"
        self.keymanager.set_password(password)
        self.assertEqual( self.keymanager.password, password )
        self.keymanager.set_password(self.password)

    def test_4_mount_drive(self):
        r = self.keymanager.mount_drive()
        self.assertTrue( r )
        self.assertTrue( self.keymanager.mounted )

    def test_3_create_drive(self):
        r = self.keymanager.create_drive()
        self.assertTrue( r )

    def test_5_umount_drive(self):
        r = self.keymanager.umount_drive()
        self.assertTrue( r )
        self.assertFalse( self.keymanager.mounted )

    def test_7_force_umount_drive(self):
        r = self.keymanager.force_umount_drive()
        self.assertTrue( r )
        self.assertFalse( self.keymanager.mounted )

    def test_6_generate_and_save_keys(self):
        r = self.keymanager.generate_and_save_keys_for_client('test')
        self.assertTrue( r )

    def test_8_has_drive(self):
        try:
            r = self.keymanager.has_drive()
            self.assertTrue( r )
        except IOError, e:
            pass







if __name__ == "__main__":
    unittest.main()

