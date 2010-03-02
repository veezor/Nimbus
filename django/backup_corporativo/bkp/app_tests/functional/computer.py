#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import join

from keymanager import KeyManager

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.app_tests.functional.system import SystemViewTest
from backup_corporativo.bkp.app_tests.functional.strongbox import StrongboxViewTest

class ComputerViewTest(NimbusTest):
    
    def test_computer(self):
        response  = self.get("/computer/new")

    def test_computer_create(self):
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
        self.client_path = km.get_client_path(comp.computer_name)
        key_path = join(self.client_path, 'client.key')
        pem_path = join(self.client_path, 'client.pem')
        cert_path = join(self.client_path, 'client.cert')
        self.assertTrue(os.access(key_path, os.R_OK))
        self.assertTrue(os.access(pem_path, os.R_OK))
        self.assertTrue(os.access(cert_path, os.R_OK))

    def test_computer_view(self):
        gconf_test = SystemViewTest()
        gconf_test.set_client(self.client)
        gconf_test.test_system_config_update()
        self.test_computer_create()

        self.assertEquals(Computer.objects.count(), 1)
        
        response = self.get( "/computer/1" )
        response = self.get( "/computer/1/edit" )
        response = self.get( "/computer/1/config/" )
        response = self.get( "/computer/1/backup/new" )
        response = self.get( "/computer/1/config/")        
        config_r = self.post( "/computer/1/file/dump", dict(file_type="config"))
        key_r = self.post( "/computer/1/file/dump", dict(file_type="key"))
        cert_r=self.post("/computer/1/file/dump", dict(file_type="certificate"))
        pem_r = self.post( "/computer/1/file/dump", dict(file_type="pem"))
        
        key = self.get_file_name('key')
        certificate = self.get_file_name('certificate')
        pem = self.get_file_name('pem')

        emsg='arquivo "%s" baixado através do sistema é diferente do existente'
        self.assertEquals(key, key_r.content, msg=emsg % 'key')
        self.assertEquals(pem, pem_r.content, msg=emsg % 'pem')
        self.assertEquals(certificate,cert_r.content,msg=emsg%'certificate')

    def get_file_name(self, type):
        file_name = Computer.FILE_NAMES[type]
        file_path = '%s/%s' % (self.client_path,file_name)
        file_content = open(file_path, 'r') 
        return file_content.read()
