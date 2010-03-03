#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import random
import pytz

from django.contrib.auth.models import User

from backup_corporativo.bkp.tests import NimbusTest

class SystemViewTest(NimbusTest):
    
    def test_system(self):
        self.get("/system/config/edit")
        self.get("/system/network/")

    def test_system_config_update(self):
        response = self.post_and_test( "/system/config/update",
                                       "gconfig",
                                       dict( globalconfig_name="test",
                                             director_port=2000,
                                             storage_port=2001,
                                             total_backup_size=1000,
                                             offsite_on = False )),

    def test_system_network_update(self):
        response = self.post_and_test( "/system/network/update",
                                       "iface",
                                       dict( interface_name = "test0",
                                             interface_address = "192.168.1.101",
                                             interface_network = "192.168.1.0",
                                             interface_gateway = "192.168.1.1",
                                             interface_netmask = "255.255.255.0",
                                             interface_broadcast = "192.168.1.255",
                                             interface_dns1 = "192.168.1.1",
                                             interface_dns2 = "192.168.1.2"))

    def test_system_password_edit(self):
        self.get( "/system/password/edit")
        self.post( "/system/password/update", 
                   dict(old_password="test",
                        new_password1="testing",
                        new_password2="testing") )
        user = User.objects.get(pk=1)
        self.assertTrue(user.check_password("testing"))

    def test_offsite(self):
        self.test_system_config_update()
        self.get("/system/offsite/edit")
        self.post("/system/offsite/enable",
                  dict(offsite_on=True,
                       offsite_hour="00:00:00"))
        self.post("/system/offsite/disable", {})

    def test_ping(self):
        response = self.post( "/system/network/ping/create",
                              dict(ping_address="127.0.0.1") )

    def test_traceroute(self):
        response = self.post( "/system/network/traceroute/create",
                              dict(traceroute_address="127.0.0.1") )

    def test_nslookup(self):
        response = self.post( "/system/network/nslookup/create",
                              dict(nslookup_address="127.0.0.1") )

    def test_timezone(self):
        
        country = random.choice(pytz.country_names.keys())
        area = pytz.country_timezones[country]
        
        old_tz = time.strftime("%Z")
        
        response = self.post( "/system/time/update",
                              dict( ntp_server="a.ntp.br",
                                    tz_country=country,
                                    tz_area=area ) )
        
        current_tz = time.strftime("%Z")
        self.assertNotEqual(old_tz, current_tz)