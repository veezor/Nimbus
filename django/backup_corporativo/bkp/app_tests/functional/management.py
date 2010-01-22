#!/usr/bin/python
# -*- coding: utf-8 -*-

from backup_corporativo.bkp.tests import NimbusTest


class ManagementViewTest(NimbusTest):

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
