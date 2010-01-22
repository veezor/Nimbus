#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import management

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import Computer

class ComputerViewTest(NimbusTest):
    
    def test_computer(self):
        response  = self.get("/computer/new")

    def test_computer_create(self):
        response = self.post( "/computer/create",
                               dict( computer_name="computer_test",
                                     computer_ip = "192.168.1.102",
                                     computer_so = "UNIX",
                                     computer_description = "test"))
        self.assertEquals(Computer.objects.count(), 1)

    def test_computer_view(self):
        management.call_command('loaddata', 'computer.json', verbosity=0)

        self.assertEquals(Computer.objects.count(), 1)
        response = self.get( "/computer/1" )
        response = self.get( "/computer/1/edit" )
        response = self.get( "/computer/1/config/" )
        response = self.get( "/computer/1/backup/new" )
        response = self.post( "/computer/1/config/dump", {})
        response = self.get( "/computer/1/config/")
