#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import join
from django.core import management

from keymanager import KeyManager

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import Computer

class ComputerViewTest(NimbusTest):
    
    def test_computer(self):
        response  = self.get("/computer/new")

    def test_computer_create(self):
        from backup_corporativo.bkp.app_tests.functional.strongbox import StrongboxViewTest
        sbox_test = StrongboxViewTest()
        sbox_test.set_client(self.client)
        sbox_test.test_mount_strongbox()
        km = KeyManager()
    
        response = self.post( "/computer/create",
                               dict( computer_name="computer_test",
                                     computer_ip = "192.168.1.102",
                                     computer_so = "UNIX",
                                     computer_description = "test"))
        self.assertEquals(Computer.objects.count(), 1)
        
        comp = Computer.objects.get(pk=1)
        client_path = km.get_client_path(comp.computer_name)
        key_path = join(client_path, 'client.key')
        pem_path = join(client_path, 'client.pem')
        cert_path = join(client_path, 'client.cert')
        self.assertTrue(os.access(key_path, os.R_OK))
        self.assertTrue(os.access(pem_path, os.R_OK))
        self.assertTrue(os.access(cert_path, os.R_OK))

    def test_computer_view(self):
        management.call_command('loaddata', 'computer.json', verbosity=0)

        self.assertEquals(Computer.objects.count(), 1)
        response = self.get( "/computer/1" )
        response = self.get( "/computer/1/edit" )
        response = self.get( "/computer/1/config/" )
        response = self.get( "/computer/1/backup/new" )
        response = self.post( "/computer/1/config/dump", {})
        response = self.get( "/computer/1/config/")
