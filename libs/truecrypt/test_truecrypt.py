#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import truecrypt
import os






class TrueCryptTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.truecrypt = truecrypt.TrueCrypt(debug=True)
        self.filedrive = "/tmp/drive.crypto"
        self.mountpoint = "/tmp/drivetest"
        self.password = '1234'
        self.new_password = "4567"
        self.fileback = '/tmp/drive.crypto.back'

    def test_1_create_drive(self):
        r = self.truecrypt.create_drive(self.password, self.filedrive)
        self.assertTrue(r)

    def test_get_popen(self):
        popen = self.truecrypt._get_popen(["echo","test"])
        stdout, stdin = popen.communicate()
        self.assertEqual( stdout, 'test\n')
    
    def test_generate_list(self):
        genlist = self.truecrypt._generate_list("create", self.password, self.filedrive)
        cmd = " ".join(genlist)

        self.assertEqual( cmd,
                         truecrypt.COMMANDS['create'] % ( self.password,
                                                          self.filedrive))



    def test_2_1_mount_drive(self):

        try:
            os.mkdir(self.mountpoint)
        except OSError, e:
            pass #silent file exists
        

        r = self.truecrypt.mount_drive(self.password, self.filedrive, self.mountpoint)
        self.assertTrue(r)

    def test_2_2_is_mounted(self):
        r = self.truecrypt.is_mounted(self.filedrive)
        self.assertTrue(r)


    def test_3_umount_drive(self):
        r = self.truecrypt.umount_drive( self.filedrive )
        self.assertTrue(r)

    def test_6_umountf_drive(self):
        self.test_2_1_mount_drive()
        r = self.truecrypt.umountf_drive( self.filedrive )
        self.assertTrue(r)

    def test_4_make_backup(self):
        r = self.truecrypt.make_backup(self.password, self.fileback, self.filedrive)
        self.assertTrue(r)


    def test_5_restore_backup(self):
        r = self.truecrypt.restore_backup(self.password, self.fileback, self.filedrive)
        self.assertTrue(r)

    def test_7_password_error(self):
        self.password = "error"
        self.assertRaises( truecrypt.PasswordError, self.truecrypt.mount_drive,
                           self.password, self.filedrive, self.mountpoint )


    def test_8_change_drive_password(self):
        r = self.truecrypt.change_password( self.password, 
                                                  self.new_password,
                                                  self.filedrive)
        self.password = self.new_password
        self.test_2_1_mount_drive()
        self.assertTrue(r)



if __name__ == "__main__":
    unittest.main()

