#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import management

from backup_corporativo.bkp.tests import NimbusTest
from backup_corporativo.bkp.models import WeeklyTrigger, MonthlyTrigger, Schedule

class ScheduleViewTest(NimbusTest):
    
    def test_schedule_new(self):
        management.call_command('loaddata', 'procedure.json', verbosity=0)

        self.get("/procedure/1/schedule/new")
        response = self.post("/procedure/1/schedule/create",
                             dict( level="Incremental",
                                   schedule_type="Weekly",
                                   hour="00:00:00",
                                   sunday=True ))
        self.assertEqual(Schedule.objects.count(), 1  )
        self.assertEqual(WeeklyTrigger.objects.count(), 1  )
        trigger = WeeklyTrigger.objects.get(pk=1)
        self.assertTrue(trigger.sunday)
        self.assertEqual(trigger.level, "Incremental")
        response = self.post("/procedure/1/schedule/create",
                             dict( level="Incremental",
                                   schedule_type="Monthly",
                                   hour="00:00:00",
                                   target_days="1;2;3;4;5;6" ))
        self.assertEqual(Schedule.objects.count(), 2)
        self.assertEqual(MonthlyTrigger.objects.count(), 1)

    def test_schedule_update(self):
        management.call_command('loaddata', 'schedule.json', verbosity=0)
        
        self.get("/schedule/1/edit")
        response = self.post("/schedule/1/update",
                             dict( level="Full",
                                   hour="01:00:00",
                                   monday=True ))
        trigger = WeeklyTrigger.objects.get(pk=1)
        self.assertTrue(trigger.monday)
        self.assertEqual(trigger.level, "Full")
        response = self.post("/schedule/2/update",
                             dict( level="Full",
                                   hour="01:00:00",
                                   target_days="5;6" ))
        trigger = MonthlyTrigger.objects.get(pk=1)
        self.assertEqual(trigger.level, "Full")
        self.assertEqual(trigger.target_days, "5;6")

    def test_schedule_delete(self):
        management.call_command('loaddata', 'schedule.json', verbosity=0)
        
        self.get("/schedule/1/delete")
        size = Schedule.objects.count()
        self.post("/schedule/1/delete", {})
        new_size = Schedule.objects.count()
        self.assertEqual(new_size, size - 1)
