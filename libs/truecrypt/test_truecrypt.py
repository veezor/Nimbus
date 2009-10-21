#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import truecrypt
from mock import Mock
import os


class TrueCryptMockTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.truecrypt = truecrypt.TrueCrypt()
        self.mock = Mock()
        truecrypt.TrueCrypt._get_popen = self.mock
        
        self.psword = '1234'
        self.drive = '/tmp/drive.crypto'
        self.fileback = '/tmp/drive.crypto.back'


    def test_call_commands(self):
        self.truecrypt.call_command("create", self.psword, self.drive)

        self.assertTrue(self.mock.called)

        call_arg = " ".join( self.mock.call_args[0][0] )
        self.assertEqual(call_arg,
                         truecrypt.COMMANDS['create'] % ( self.psword,
                                                          self.drive))


    def test_make_backup(self):
        self.truecrypt.make_backup(self.psword, self.fileback)


    def test_restore_backup(self):
        self.truecrypt.restore_backup(self.psword, self.fileback)



class TrueCryptTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        reload(truecrypt) # remove mock
        self.truecrypt = truecrypt.TrueCrypt()
        self.assertFalse( isinstance(truecrypt.TrueCrypt._get_popen, Mock) )
        self.filedrive = "/tmp/drive.crypto"
        self.mountpoint = "/tmp/drivetest"
        self.password = '1234'
        self.fileback = '/tmp/drive.crypto.back'

    def test_create_drive(self):
        r = self.truecrypt.create_drive(self.password, self.filedrive)
        self.assertTrue(r)


    def mount_drive(self):

        try:
            os.mkdir(self.mountpoint)
        except OSError:
            pass #silent file exists

        r = self.truecrypt.mount_drive(self.password, self.filedrive, self.mountpoint)
        self.assertTrue(r)


    def test_umount_drive(self):
        self.mount_drive()
        r = self.truecrypt.umount_drive( self.filedrive )
        self.assertTrue(r)

    def test_umountf_drive(self):
        self.mount_drive()
        r = self.truecrypt.umountf_drive( self.filedrive )
        self.assertTrue(r)

    def test_make_backup(self):
        r = self.truecrypt.make_backup(self.password, self.fileback, self.filedrive)
        self.assertTrue(r)


    def test_restore_backup(self):
        self.test_make_backup()
        r = self.truecrypt.restore_backup(self.password, self.fileback, self.filedrive)
        self.assertTrue(r)



if __name__ == "__main__":
    unittest.main()

