#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import unittest


from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

import truecrypt


class NimbusUnitTest(unittest.TestCase):
    files_to_remove = []
    
    def tearDown(self):
        for fpath in self.files_to_remove:
            try:
                os.remove(fpath)
            except OSError:
                pass


class NimbusTest(TestCase):

    def runTest(self):
        pass

    def set_client(self, client):
        self.client = client

    def setUp(self):
        TestCase.setUp(self)
        self.client = Client()
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
                             "Field %s.%s: %s != %s" % ( itemname, key, 
                                                         attr, value) )
        return response

from backup_corporativo.bkp.app_tests.unit.system import SystemUnitTest
from backup_corporativo.bkp.app_tests.unit.fileset import FilesetUnitTest
from backup_corporativo.bkp.app_tests.unit.computer import ComputerUnitTest
from backup_corporativo.bkp.app_tests.functional.strongbox import StrongboxViewTest
from backup_corporativo.bkp.app_tests.functional.management import ManagementViewTest
from backup_corporativo.bkp.app_tests.functional.system import SystemViewTest
from backup_corporativo.bkp.app_tests.functional.computer import ComputerViewTest
from backup_corporativo.bkp.app_tests.functional.procedure import ProcedureViewTest
from backup_corporativo.bkp.app_tests.functional.restore import RestoreViewTest
from backup_corporativo.bkp.app_tests.functional.schedule import ScheduleViewTest
from backup_corporativo.bkp.app_tests.functional.fileset import FileSetViewTest
