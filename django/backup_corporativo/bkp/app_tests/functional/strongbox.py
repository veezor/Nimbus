#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import truecrypt

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import HeaderBkp


class StrongboxViewTest(NimbusTest):
    
    def runTest(self):
         pass
    
    def set_client(self, client):
        self.client = client
    
    def test_create_strongbox(self):
        self.post( "/management/strongbox/create", 
                   dict( sb_password="test", 
                         sb_password_2="test"))
        r = os.access(truecrypt.DRIVEFILE, os.R_OK)
        self.assertTrue(r)
        
    def test_mount_strongbox(self):
        self.test_create_strongbox()
        self.post( "/management/strongbox/mount",
                   { "sb_password" : "test" } )

    def test_umount_strongbox(self):
        self.test_create_strongbox()
        self.test_mount_strongbox()
        self.post( "/management/strongbox/umount",
                   { "sb_forceumount" : True } )

    def test_headerbkp(self):
        self.test_mount_strongbox()
        self.gets( [ "/strongbox/headerbkp/list",
                     "/strongbox/headerbkp/new"  ])
        self.post( "/strongbox/headerbkp/create",
                   dict( drive_password="test",
                         headerbkp_name="testing" ) )
        self.assertEqual(HeaderBkp.objects.count(), 1 )
        self.post( "/strongbox/headerbkp/1/update",
                   {"headerbkp_name":"testing"})
        self.gets( ["/strongbox/headerbkp/1/edit", 
                    "/strongbox/headerbkp/1/restore",
                    "/strongbox/headerbkp/1/delete"] )

#        self.post( "/management/strongbox/changepwd",
#                   dict( old_password="test",
#                         new_password="test2",
#                         new_password_2="test2"))



