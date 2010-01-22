#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import management
from backup_corporativo.bkp.tests import NimbusTest


class RestoreViewTest(NimbusTest):
    
    def test_restore_new(self):
        management.call_command('loaddata', 'computer.json', verbosity=0)
        
        self.get("/restore/new")
        response = self.post("/restore/create", 
                             dict(target_client=1))

    def test_restore_computer(self):
        management.call_command('loaddata', 'procedure.json', verbosity=0)        

        self.get("/computer/1/restore/new")
        response = self.post( "/computer/1/restore/create", 
                              dict(target_procedure=1))
