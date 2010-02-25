#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import management

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import Procedure, FileSet


class ProcedureViewTest(NimbusTest):
    
    def test_procedure_create(self):
        management.call_command('loaddata', 'computer.json', verbosity=0)

        self.post( "/computer/1/backup/create",
                   dict(offsite_on=True,
                        procedure_name="test",
                        storage=1,
                        path="c:/test/",
                        pool_size="1000 M",
                        retention_time=30))
        self.assertEqual(Procedure.objects.count(), 1)
        self.assertEqual(FileSet.objects.count(), 1)

    def test_procedure_update(self):
        management.call_command('loaddata', 'procedure.json', verbosity=0)

        self.get("/procedure/1/backup/edit")

        response = self.post( "/procedure/1/backup/update",
                              dict( procedure_name="test2",
                                    offsite_on=False,
                                    storage=1,
                                    pool_size="1000 M",
                                    retention_time=30))
        procedure = response.context['proc']
        self.assertEqual(procedure.procedure_name, "test2")
        self.assertEqual(procedure.offsite_on, False)
        self.assertEqual(procedure.storage.id, 1)

    def test_procedure_delete(self):
        management.call_command('loaddata', 'procedure.json', verbosity=0)

        self.get("/procedure/1/delete")
        self.post("/procedure/1/delete", {})
        self.assertEqual(Procedure.objects.count(), 0)
