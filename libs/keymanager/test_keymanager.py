#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import tempfile
import unittest
import keymanager


class KeyManagerTest(unittest.TestCase):

    def setUp(self):
        self.patch_file = mock.patch('__builtin__.file')
        self.file_mock = self.patch_file.start()
        self.file_mock.return_value = self.file_mock
        self.file_mock.__enter__.return_value = self.file_mock
        self.patch_popen = mock.patch('subprocess.Popen')
        self.popen_mock = self.patch_popen.start()


    def tearDown(self):
        self.patch_file.stop()
        self.patch_popen.stop()


    def test_generate_pem(self):
        key = "a"
        certificate = "b"
        self.assertEquals(keymanager.generate_pem(key, certificate), key+certificate)


    def test_generate_key(self):
        filename = tempfile.mktemp()
        expected_key = "key content"

        self.file_mock.read.return_value = expected_key

        key = keymanager.generate_key(filename)
        self.assertEquals(key, expected_key)



    def test_generate_certificate(self):
        filename = tempfile.mktemp()
        key_filename = tempfile.mktemp()
        expected_certificate = "certificate"

        self.file_mock.read.return_value = expected_certificate

        certificate = keymanager.generate_certificate(key_filename, filename, {})
        self.assertEquals( certificate, expected_certificate )




    def test_generate_all_keys(self):
        prefix = tempfile.mktemp()

        self.file_mock.read.return_value = "value"

        key, cert, pem = keymanager.generate_all_keys({}, prefix)

        self.assertEquals( cert, "value" )
        self.assertEquals( key, "value" )
        self.assertEquals( pem, "value"*2 )



    def test_generate_all_keys_prefix(self):
        prefix = tempfile.mktemp()

        self.file_mock.read.return_value = "value"

        key, cert, pem = keymanager.generate_all_keys({}, prefix)

        first_call = self.file_mock.call_args_list[0]
        second_call = self.file_mock.call_args_list[1]

        self.assertTrue( prefix in first_call[0][0] )
        self.assertTrue( prefix in second_call[0][0] )






if __name__ == "__main__":
    unittest.main()

