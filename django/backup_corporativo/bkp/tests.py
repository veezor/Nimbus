from django.test import TestCase
from django.contrib.auth.models import User

from backup_corporativo.bkp import models

import truecrypt

import pdb, os


class NimbusTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        test = User(username="test")
        test.set_password("test")
        test.save()
        self.client.login(username='test', password='test')
        try:
            os.remove(truecrypt.DRIVEFILE) # remove drive file
        except OSError, e:
            pass

    def get(self, url):
        response = self.client.get(url, follow=True)
        self.failUnlessEqual(response.status_code, 200, 
                             "url=%s %d!=%d" % ( url, 
                                                 response.status_code, 
                                                 200))
        return response

    def gets(self, urls):
        return [ self.get(url) for url in urls ]


    def post(self, url, data):
        response = self.client.post(url, data, follow=True)
        self.failUnlessEqual(response.status_code, 200)
        return response


    def post_and_test( self, url, itemname, data ):
        response = self.post(url, data)
        item = response.context[itemname]
        for key,value in data.items():
            attr = getattr( item, key )
            self.assertEqual( attr, value, 
                             "Field %s: %s != %s" % (itemname, attr, value) )
        return response






class NimbusViewTest(NimbusTest):

    def test_management(self):
        self.gets( ["/management/",
                         "/management/computers/list",
                         "/management/storages/list",
                         "/management/encryptions/list",
                         "/management/encryptions/new",
                         "/management/strongbox/",
                         "/management/strongbox/new",
                         "/management/strongbox/umount",
                         "/management/strongbox/changepwd",
                         ])


    def test_strongbox(self):
        self.gets( [ "/strongbox/headerbkp/list",
                     "/strongbox/headerbkp/new"  ])

        self.post( "/management/strongbox/create", 
                   dict( sb_password="test", 
                         sb_password_2="test"))

        r = os.access(truecrypt.DRIVEFILE, os.R_OK)
        self.assertTrue(r)

        self.post( "/management/strongbox/mount",
                   { "sb_password" : "test" } )


        # FIX:  ENCRYPTIONS
        self.test_computer_create()
        self.post( "/management/encryptions/create",
                   {"computer" : 1})




        self.post( "/strongbox/headerbkp/create",
                   dict( drive_password="test",
                         headerbkp_name="testing" ) )

        self.assertEqual( len(models.HeaderBkp.objects.all()), 1 )


        self.post( "/strongbox/headerbkp/1/update",
                   {"headerbkp_name":"testing"})

        self.gets( ["/strongbox/headerbkp/1/edit", 
                    "/strongbox/headerbkp/1/restore",
                    "/strongbox/headerbkp/1/delete"] )



        self.post( "/management/strongbox/umount",
                   { "sb_forceumount" : True } )

#        self.post( "/management/strongbox/changepwd",
#                   dict( old_password="test",
#                         new_password="test2",
#                         new_password_2="test2"))
#
    



    def test_system(self):
        self.get("/system/config/edit")
        self.get("/system/network/")

    def test_system_config_update(self):
        response = self.post_and_test( "/system/config/update",
                                       "gconfig",
                                       dict( globalconfig_name="test",
                                             director_port=2000,
                                             storage_port=2001,
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


    def test_computer(self):
        response  = self.get("/computer/new")

    def test_computer_create(self):
        response = self.post( "/computer/create",
                               dict( computer_name="computer_test",
                                     computer_ip = "192.168.1.102",
                                     computer_so = "UNIX",
                                     computer_description = "test"))

        self.assertEquals( len(models.Computer.objects.all()), 1)


    def test_computer_view(self):
        self.test_computer_create()
        self.test_system_config_update()
        self.assertEquals( len(models.Computer.objects.all()), 1)
        response = self.get( "/computer/1" )
        response = self.get( "/computer/1/edit" )
        response = self.get( "/computer/1/config/" )
        response = self.get( "/computer/1/backup/new" )
        
        response = self.post( "/computer/1/config/dump", {})
        response = self.get( "/computer/1/config/")



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


    def test_session(self):
        self.gets( [ "/session/",
                     "/session/new",
                     "/session/delete"] )
        self.post("/session/delete", {})

        self.post("/session/", 
                  dict(auth_login="test",
                       auth_password="test"))


    def test_ping(self):
        response = self.post( "/system/network/ping/create",
                              dict(ping_address="127.0.0.1") )

    def test_traceroute(self):
        response = self.post( "/system/network/traceroute/create",
                              dict(traceroute_address="127.0.0.1") )

    def test_nslookup(self):
        response = self.post( "/system/network/nslookup/create",
                              dict(nslookup_address="127.0.0.1") )






