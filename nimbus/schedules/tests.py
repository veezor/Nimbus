#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from django.conf import settings
from django.test import TestCase

from nimbus.schedules import models


class GenericUnicodeTest(TestCase):

    def test_backup_level(self):
        backup_level = models.BackupLevel(name="test")
        self.assertEqual(unicode(backup_level), u"test")

    def test_backup_kind(self):
        backup_kind = models.BackupKind(name="test",
                                        name_pt="teste")
        self.assertEqual(unicode(backup_kind), u"test")

    def test_schedule(self):
        schedule = models.Schedule(name="test", is_model=False)
        self.assertEqual(unicode(schedule), u"test")

    def test_run(self):
        schedule = models.Schedule(name="test", is_model=False)
        backup_kind = models.BackupKind(name="kind",
                                        name_pt="tipo")
        backup_level = models.BackupLevel(name="level")
        run = models.Run(schedule=schedule,
                         day=1,
                         hour=0,
                         minute=0,
                         level=backup_level,
                         kind=backup_kind)
        self.assertEqual(unicode(run), u"test - kind - 1 - level - 0:0")



class RunModelTest(TestCase):

    def setUp(self):
        self.schedule = models.Schedule(name="test", is_model=False)
        self.backup_kind = models.BackupKind(name="kind",
                                             name_pt="tipo")
        self.backup_level = models.BackupLevel(name="level")
        self.run = models.Run(schedule=self.schedule,
                              day=1,
                              hour=0,
                              minute=0,
                              level=self.backup_level,
                              kind=self.backup_kind)


    def test_day_string(self):
        self.backup_kind.name = "weekly"
        self.assertEqual(self.run.day_string, "Segunda-feira")
        self.run.day = 2
        self.assertEqual(self.run.day_string, "Terca-feira")
        self.backup_kind.name = "daily"
        self.assertEqual(self.run.day_string, "Todos")
        self.backup_kind.name = "hourly"
        self.assertEqual(self.run.day_string, "Todos")
        self.backup_kind.name = "monthly"
        self.assertEqual(self.run.day_string, "2") #run.day = 2


    def test_bacula_config(self):
        self.backup_kind.name = "monthly"
        self.assertEqual(self.run.bacula_config,
                         "Run = Level=level on 1 at 0:0")
        self.backup_kind.name = "weekly"
        self.assertEqual(self.run.bacula_config,
                         "Run = Level=level monday at 0:0")
        self.backup_kind.name = "daily"
        self.assertEqual(self.run.bacula_config,
                         "Run = Level=level daily at 0:0")
        self.backup_kind.name = "hourly"
        self.assertEqual(self.run.bacula_config,
                         "Run = Level=level hourly at 00:0")



EXPECTED_SCHEDULE_FILE="""\
Schedule {
    Name = "%s"
    
    Run = Level=Full monday at 0:0
    
}
"""

EXPECTED_SCHEDULE_FILE_2="""\
Schedule {
    Name = "%s"
    
    Run = Level=Full monday at 10:0
    
}
"""


class SignalsTest(TestCase):

    def setUp(self):
        self.schedule = models.Schedule(name="test", is_model=False)
        self.schedule.save()
        self.backup_kind = models.BackupKind(name="weekly",
                                             name_pt="tipo")
        self.backup_kind.save()
        self.backup_level = models.BackupLevel(name="Full")
        self.backup_level.save()
        self.run = models.Run(schedule=self.schedule,
                              day=1,
                              hour=0,
                              minute=0,
                              level=self.backup_level,
                              kind=self.backup_kind)
        self.run.save()

        name = self.schedule.bacula_name
        self.filename = os.path.join(settings.NIMBUS_SCHEDULES_DIR, name)



    def test_update_schedule_file(self):
        template = EXPECTED_SCHEDULE_FILE % self.schedule.bacula_name
        with file(self.filename) as f_obj:
            content = f_obj.read()
            self.assertMultiLineEqual( content, template )

    def test_remove_schedule_file(self):
        self.schedule.delete()
        self.assertFalse( os.path.exists(self.filename ))

    def test_update_schedule(self):
        self.run.hour = 10
        self.run.save()

        template = EXPECTED_SCHEDULE_FILE_2 % self.schedule.bacula_name
        with file(self.filename) as f_obj:
            content = f_obj.read()
            self.assertMultiLineEqual( content, template )


