#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from nimbus.base.models import BaseModel
from nimbus.shared import signals, utils, enums
from nimbus.libs.template import render_to_file


LEVELS = tuple( (l,l) for l in enums.levels )  
WEEKDAYS = tuple( (d,d) for d in enums.weekdays )
MONTHDAYS = tuple( (d,d) for d in enums.days )


class Schedule(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False)

    def _get_triggers(self):
        return list(self.hourly_set.get_query_set()) +\
                list(self.daily_set.get_query_set()) +\
                list(self.monthly_set.get_query_set()) +\
                list(self.weekly_set.get_query_set())

    def get_runs(self):
        return [ trigger.get_run() for trigger in self._get_triggers() ]



class TriggerBase(models.Model):
    schedule = models.ForeignKey(Schedule, null=False, blank=False)
    level = models.CharField(max_length="25", null=False, 
                             blank=False, choices=LEVELS)
    hour = models.TimeField( null=False, blank = False) 

    @classmethod
    def type_name(cls):
        return cls.__name__.lower()

    def __unicode__(self):
        return self.run_str()

    class Meta:
        abstract = True


class Daily(TriggerBase):
    
    def run_str(self):
        return u"%s at %s" % ( self.type_name(),
                               self.hour.strftime("%H:%M") )



class Hourly(TriggerBase):
    
    def run_str(self):
        return u"%s at 00:%s" % ( self.type_name(),
                                  self.hour.strftime("%M") )


class Monthly(TriggerBase):
    day = models.IntegerField(null=False, blank=False, choices=MONTHDAYS)


    def run_str(self):
        return u"%s %d at %s" % ( self.type_name(), 
                                  int(self.day),
                                  self.hour.strftime("%H:%M") )



class Weekly(TriggerBase):
    day = models.CharField(null=False, blank=False,
                           max_length=4, choices=WEEKDAYS)


    def run_str(self):
        return u"%s %s at %s" % ( self.type_name(), 
                                  self.day,
                                  self.hour.strftime("%H:%M") )








def update_schedule_file(schedule):

    name = schedule.bacula_name()

    filename = path.join( settings.NIMBUS_SCHEDULES_PATH, 
                          name)

    render_to_file( filename,
                    "schedule",
                    name=name,
                    runs=schedule.get_runs() )



def remove_schedule_file(schedule):
    name = schedule.bacula_name()

    filename = path.join( settings.NIMBUS_SCHEDULES_PATH, 
                          name)
    utils.remove_or_leave(filename)



signals.connect_on( update_schedule_file, Schedule, post_save)
signals.connect_on( remove_schedule_file, Schedule, post_delete)


signals.connect_on( update_schedule_file, Monthly, post_save)
signals.connect_on( update_schedule_file, Daily, post_save)
signals.connect_on( update_schedule_file, Weekly, post_save)
signals.connect_on( update_schedule_file, Hourly, post_save)

signals.connect_on( update_schedule_file, Monthly, post_delete)
signals.connect_on( update_schedule_file, Daily, post_delete)
signals.connect_on( update_schedule_file, Weekly, post_delete)
signals.connect_on( update_schedule_file, Hourly, post_delete)
