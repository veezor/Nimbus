#!/usr/bin/python
# -*- coding: utf-8 -*-

import truecrypt
import os

from backup_corporativo.bkp.models import Wizard, NetworkInterface, GlobalConfig, TimezoneConfig
from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.forms import NewStrongBoxForm

class WizardViewTest(NimbusTest):
    
    def setUp(self):
        NimbusTest.setUp(self, wiz=False)
    
    def test(self):
        response = self.post("/wizard/config/update",
                             dict(globalconfig_name = "Nome configuração",
                                  director_port = 9101,
                                  storage_port = 9103,
                                  total_backup_size= 1000,
                                  offsite_on = False))
        self.assertEquals(Wizard.objects.count(),1)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_step, 1)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_lock, 0)
        
        response = self.post("/wizard/network/update",
                             dict(interface_name = "Nome_interface",
                                  interface_address = "1.1.1.1",
                                  interface_netmask = "1.1.1.1",
                                  interface_network = "1.1.1.1",
                                  interface_broadcast = "1.1.1.1",
                                  interface_gateway = "1.1.1.1",
                                  interface_dns1 = "1.1.1.1",
                                  interface_dns2 = "1.1.1.1"))
        self.assertEquals(Wizard.objects.count(),1)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_step, 2)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_lock, 0)
        
        response = self.post("/wizard/timezone/update",
                             dict(ntp_server = "a.ntp.br",
                                  tz_country = "BD",
                                  tz_area = "Asia/Dhaka"))
        self.assertEquals(Wizard.objects.count(),1)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_step, 3)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_lock, 0)
        
        response = self.post("/wizard/strongbox/update",
                             dict(sb_password = "senha",
                                  sb_password_2 = "senha"))
        r = os.access(truecrypt.DRIVEFILE, os.R_OK)
        self.assertTrue(r)
        self.assertEquals(Wizard.objects.count(),1)
        self.assertEquals(Wizard.objects.get(pk=1).wizard_lock, 1)
        
        self.assertEquals(NetworkInterface.objects.count(), 1)
        self.assertEquals(GlobalConfig.objects.count(), 1)
        self.assertEquals(TimezoneConfig.objects.count(), 1)
