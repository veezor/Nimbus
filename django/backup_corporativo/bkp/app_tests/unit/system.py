#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from backup_corporativo.bkp.tests import NimbusUnitTest

class SystemUnitTest(NimbusUnitTest):
    
    def setUp(self):
        path = '/var/nimbus/custom/'
        self.computer = path + 'computers/'
        self.config = path + 'config/'
        self.crypt = path + 'crypt/'
        self.filesets = path + 'filesets/'
        self.header = path + 'header_bkp/'
        self.jobs = path + 'jobs/'
        self.pools = path + 'pools/'
        self.schedules = path + 'schedules/'
        self.storages = path + 'storages/'
    
    #Verifica a existencia de todos os diretórios em "/var/nimbus/custom/"
    def test_0(self):
        emsg = 'Diretório não existente: "%s"'
        self.assertTrue(os.access(self.computer,os.F_OK),msg=emsg%self.computer)
        self.assertTrue(os.access(self.config,os.F_OK),msg=emsg%self.config)
        self.assertTrue(os.access(self.crypt,os.F_OK),msg=emsg%self.crypt)
        self.assertTrue(os.access(self.filesets,os.F_OK),msg=emsg%self.filesets)
        self.assertTrue(os.access(self.header,os.F_OK),msg=emsg%self.header)
        self.assertTrue(os.access(self.jobs,os.F_OK),msg=emsg%self.jobs)
        self.assertTrue(os.access(self.pools,os.F_OK),msg=emsg%self.pools)
        self.assertTrue(os.access(self.schedules,os.F_OK),msg=emsg%self.schedules)
        self.assertTrue(os.access(self.storages,os.F_OK),msg=emsg%self.storages)
