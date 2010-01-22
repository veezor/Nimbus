#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import management

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import FileSet

class FileSetViewTest(NimbusTest):

    def test_fileset_new(self):
        management.call_command('loaddata', 'schedule.json', verbosity=0)
         
        path = "c:/test2/"
        self.get("/procedure/1/fileset/new")
        self.post("/procedure/1/fileset/create", 
                  {"path" : path} )
        self.assertEqual(FileSet.objects.count(), 2)
        fileset = FileSet.objects.get(pk=2)
        self.assertEqual(fileset.path, path)

    def test_fileset_delete(self):
        management.call_command('loaddata', 'fileset.json', verbosity=0)
            
        self.get("/fileset/1/delete")
        size = FileSet.objects.count()
        self.post("/fileset/1/delete", {})
        new_size = FileSet.objects.count()
        self.assertEqual(new_size, size - 1)
