#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
import unittest

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from django.conf import settings
from nimbus.libs import migrations
from nimbus.shared.middlewares import LogSetup

LogSetup()

class BaculaTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_update_10_to_11(self):
        with mock.patch('nimbus.libs.migrations.Computer') as mock_computer:
            with mock.patch('nimbus.libs.migrations._check_computers') as mock_check:
             with mock.patch('nimbus.libs.migrations._update_computers_crypto_info') as mock_update:
                 computers =  ["Computer1", "Computer2"]
                 mock_computer.objects.all.return_value = computers
                 migrations.update_10_to_11()
                 mock_check.assert_called_with(computers)
                 mock_update.assert_called_with(computers)

    def test_update_computers_crypt_info(self):
        with mock.patch('nimbus.libs.migrations._update_certificate_and_pem') as mock_update:
            computers =  ["Computer1", "Computer2"]
            migrations._update_computers_crypto_info(computers)
            mock_update.assert_any_call(computers[0])
            mock_update.assert_any_call(computers[1])



    def test_check_computers(self):
        with mock.patch('nimbus.libs.migrations._computer_is_online') as mock_is_online:
            computers =  ["Computer1", "Computer2"]
            mock_is_online.return_value = True
            migrations._check_computers(computers)
            mock_is_online.assert_any_call(computers[0])
            mock_is_online.assert_any_call(computers[1])
            mock_is_online.side_effect = [True, False]
            self.assertRaises(migrations.ComputerUpdateError, migrations._check_computers, computers)


    def test_computer_is_online(self):
        computer = mock.Mock()
        value = migrations._computer_is_online(computer)
        self.assertTrue(value)
        computer.get_file_tree.side_effect = TypeError
        value = migrations._computer_is_online(computer)
        self.assertFalse(value)


    def test_update_certificate_and_pem(self):
        with mock.patch('nimbus.libs.migrations.keymanager') as mock_keymanager:
            with mock.patch('nimbus.libs.migrations.tempfile') as mock_tempfile:
                files =  ["file1", "file2"]
                mock_tempfile.mktemp.side_effect = files
                mock_keymanager.generate_certificate.return_value = "certificate"
                mock_keymanager.generate_pem.return_value = "pem"
                computer = mock.Mock()
                crypto_info = mock.Mock()
                computer.crypto_info = crypto_info
                migrations._update_certificate_and_pem(computer)
                crypto_info.save_key.assert_called_with(files[0])
                mock_keymanager.generate_certificate.assert_called_with( "file1",
                                                                         "file2",
                                                                          settings.NIMBUS_SSLCONFIG)
                crypto_info.save.assert_called_with()
                computer.configure.assert_called_with()
                self.assertEqual(crypto_info.certificate, "certificate")
                self.assertEqual(crypto_info.pem, "pem")



if __name__ == "__main__":
    unittest.main()

