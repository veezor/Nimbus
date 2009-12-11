from django.test import TestCase
from django.contrib.auth.models import User
import pdb


class NimbusTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        test = User(username="test")
        test.set_password("test")
        test.save()
        self.client.login(username='test', password='test')

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
                         "/management/strongbox/",
                         "/management/strongbox/umount",
                         "/management/strongbox/changepwd",
                         ])


    def test_strongbox(self):
        self.gets( ["/strongbox/headerbkp/list",
                         "/strongbox/headerbkp/new" 
                        ])


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








