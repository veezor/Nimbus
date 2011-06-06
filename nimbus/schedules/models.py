#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from nimbus.base.models import BaseModel
from nimbus.shared import signals, utils, enums, fields
from nimbus.libs.template import render_to_file


LEVELS = tuple( (l,l) for l in enums.levels )  
WEEKDAYS = tuple( (d,d) for d in enums.weekdays )
MONTHDAYS = tuple( (d,d) for d in enums.days )


class BackupLevel(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __unicode__(self):
        return self.name


class Schedule(BaseModel):
    name = models.CharField(u'Nome qualquer', max_length=255, null=False, blank=False)
    is_model = models.BooleanField(default=False, null=False)

    def __unicode__(self):
        return self.name

    def if_month(self):
        try:
            return self.month
        except:
            return None

    def if_week(self):
        try:
            return self.week
        except:
            return None

    def if_day(self):
        try:
            return self.day
        except:
            return None

    def if_hour(self):
        try:
            return self.hour
        except:
            return None



class Month(models.Model):
    active = models.BooleanField(default=True)
    schedule = models.OneToOneField(Schedule)
    days = models.CommaSeparatedIntegerField(null=False, max_length=255)
    hour = models.TimeField()
    level = models.ForeignKey(BackupLevel)

    def __unicode__(self):
        return self.schedule.name


class Week(models.Model):
    active = models.BooleanField(default=True)
    schedule = models.OneToOneField(Schedule)
    days = models.CommaSeparatedIntegerField(null=False, max_length=255)
    hour = models.TimeField()
    level = models.ForeignKey(BackupLevel)

    def __unicode__(self):
        return self.schedule.name


class Day(models.Model):
    active = models.BooleanField(default=True)
    schedule = models.OneToOneField(Schedule)
    hour = models.TimeField()
    level = models.ForeignKey(BackupLevel)

    def __unicode__(self):
        return self.schedule.name


class Hour(models.Model):
    active = models.BooleanField(default=True)
    schedule = models.OneToOneField(Schedule)
    minute = models.PositiveSmallIntegerField()
    level = models.ForeignKey(BackupLevel)

    def __unicode__(self):
        return self.schedule.name


# class Schedule(BaseModel):
#     name = models.CharField(max_length=255, unique=True, null=False,
#                              validators=[fields.check_model_name])
# 
#     def get_triggers(self):
#         return list(self.hourly_set.get_query_set()) +\
#                 list(self.daily_set.get_query_set()) +\
#                 list(self.monthly_set.get_query_set()) +\
#                 list(self.weekly_set.get_query_set())
# 
# 
#     def get_monthly_hour(self): #FIX: remove this
#         if self.monthly_set.count():
#             return self.monthly_set.all()[0].hour
# 
#     def get_weekly_hour(self): #FIX: remove this
#         if self.weekly_set.count():
#             return self.weekly_set.all()[0].hour
# 
# 
#     def get_runs(self):
#         return [ trigger.get_run() for trigger in self.get_triggers() ]
# 
# 
#     def __unicode__(self):
#         return self.name



# class TriggerBase(models.Model):
#     schedule = models.ForeignKey(Schedule, null=False, blank=False)
#     level = models.CharField(max_length="25", null=False, 
#                              blank=False, choices=LEVELS)
#     hour = models.TimeField( null=False, blank = False) 
# 
#     @classmethod
#     def type_name(cls):
#         return cls.__name__.lower()
# 
#     def __unicode__(self):
#         return self.get_run()
# 
#     class Meta:
#         abstract = True
# 
# 
# class Daily(TriggerBase):
#     
#     def get_run(self):
#         return u"%s at %s" % ( self.type_name(),
#                                self.hour.strftime("%H:%M") )
# 
# 
# 
# class Hourly(TriggerBase):
#     
#     def get_run(self):
#         return u"%s at 00:%s" % ( self.type_name(),
#                                   self.hour.strftime("%M") )
# 
# 
# class Monthly(TriggerBase):
#     day = models.IntegerField(null=False, blank=False, choices=MONTHDAYS)
# 
# 
#     def get_run(self):
#         return u"%s %d at %s" % ( self.type_name(), 
#                                   int(self.day),
#                                   self.hour.strftime("%H:%M") )
# 
# 
# 
# class Weekly(TriggerBase):
#     day = models.CharField(null=False, blank=False,
#                            max_length=4, choices=WEEKDAYS)
# 
# 
#     def get_run(self):
#         return u"%s %s at %s" % ( self.type_name(), 
#                                   self.day,
#                                   self.hour.strftime("%H:%M") )








def update_schedule_file(schedule):

    name = schedule.bacula_name

    filename = path.join( settings.NIMBUS_SCHEDULES_DIR, 
                          name)

    render_to_file( filename,
                    "schedule",
                    name=name,
                    runs=schedule.get_runs() )



def remove_schedule_file(schedule):
    name = schedule.bacula_name
    filename = path.join( settings.NIMBUS_SCHEDULES_DIR, name)
    utils.remove_or_leave(filename)



def update_schedule(trigger):
    update_schedule_file(trigger.schedule)
    

# signals.connect_on( update_schedule_file, Schedule, post_save)
# signals.connect_on( remove_schedule_file, Schedule, post_delete)
# 
# 
# signals.connect_on( update_schedule, Monthly, post_save)
# signals.connect_on( update_schedule, Daily, post_save)
# signals.connect_on( update_schedule, Weekly, post_save)
# signals.connect_on( update_schedule, Hourly, post_save)
# 
# signals.connect_on( update_schedule, Monthly, post_delete)
# signals.connect_on( update_schedule, Daily, post_delete)
# signals.connect_on( update_schedule, Weekly, post_delete)
# signals.connect_on( update_schedule, Hourly, post_delete)