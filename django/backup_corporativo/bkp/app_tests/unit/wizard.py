#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backup_corporativo.bkp.models import Wizard, NetworkInterface, GlobalConfig
from backup_corporativo.bkp.tests import NimbusUnitTest

class WizardUnitTest(NimbusUnitTest):
    
    def _create_wizard_1(self):
        self.wizard1, created = Wizard.objects.get_or_create(
                        wizard_step = 1,
                        wizard_lock = 0,
                        globalconfig_name = "GlobalNome",
                        director_port = 9101,
                        storage_port = 9103,
                        total_backup_size = 1000,
                        offsite_on = 0,
                        )
        
    def _create_wizard_2(self):
        self.wizard, created = Wizard.objects.get_or_create(
                        wizard_step = 2,
                        wizard_lock = 0,
                        globalconfig_name = "GlobalNome",
                        director_port = 9101,
                        storage_port = 9103,
                        total_backup_size = 1000,
                        offsite_on = 0,
                        interface_name = "InterfaceNome",
                        interface_address = "10.0.2.15",
                        interface_netmask = "255.255.255.0",
                        interface_network = "10.0.2.30",
                        interface_broadcast = "10.0.2.255",
                        interface_gateway = "10.0.2.244",
                        interface_dns1 = "10.0.2.100",
                        interface_dns2 = "10.0.2.200"
                        )
            
    def _create_wizard_3(self):
        self.wizard, created = Wizard.objects.get_or_create(
                        wizard_step = 2,
                        wizard_lock = 1,
                        globalconfig_name = "GlobalNome",
                        director_port = 9101,
                        storage_port = 9103,
                        total_backup_size = 1000,
                        offsite_on = 0,
                        interface_name = "InterfaceNome",
                        interface_address = "10.0.2.15",
                        interface_netmask = "255.255.255.0",
                        interface_network = "10.0.2.30",
                        interface_broadcast = "10.0.2.255",
                        interface_gateway = "10.0.2.244",
                        interface_dns1 = "10.0.2.100",
                        interface_dns2 = "10.0.2.200"
                        )