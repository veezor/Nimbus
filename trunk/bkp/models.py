#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
import os
import string

# TODO
# add computer attribute password
# auto generate computer password
# update def update_computer_file(instance): with computer password

### Constants ###
TYPE_CHOICES = (
    ('Weekly', 'Weekly'),
    ('Monthly', 'Monthly'),
    ('Unique','Unique'),
)

LEVEL_CHOICES = (
    ('Full', 'Full'),
    ('Incremental', 'Incremental'),
)

DAYS_OF_THE_WEEK = (
    'sunday','monday','tuesday',
    'wednesday','thursday','friday',
    'saturday',
)


###
###   Models
###


### Computer ###

class Computer(models.Model):
    name = models.CharField("Nome",max_length=50)
    ip = models.IPAddressField("Endereço IP")
    description = models.CharField("Descrição",max_length=100)
    
    # get list of associated procedures
    def procedures_list(self):
        return Procedure.objects.filter(computer=self.id)

    def get_computer_name(self):
        return str.lower(str(self.name))

    def __unicode__(self):
        return self.name
        
### Procedure ###

class Procedure(models.Model):
    computer = models.ForeignKey(Computer)
    name = models.CharField(max_length=50)
    restore_path = models.CharField(max_length="255")
    status = models.CharField(max_length=10, default="Invalid")

    # change status to valid or invalid depending if filesets_list() returns the list or an empty set
    def update_status(self):
        self.status = self.filesets_list() and 'Valid' or 'Invalid'
        self.save()
    
    # get list of associated file sets    
    def filesets_list(self):
        return FileSet.objects.filter(procedure=self.id)

    # get list of associated schedules
    def schedules_list(self):
        return Schedule.objects.filter(procedure=self.id)

    # get list of associated pools        
    def pools_list(self):
        return Pool.objects.filter(procedure=self.id)
    
    # get fileset name for bacula file
    def get_fileset_name(self):
        return "%s_Set" % (self.name)
        
    # get procedure name for bacula file    
    def get_procedure_name(self):
        return "%s_Job" % (self.name)
    
    # get restore procedure name for bacula    
    def get_restore_name(self):
        return "%s_RestoreJob" % (self.name)
        
    # get schedule name for bacula file       
    def get_schedule_name(self):
        return "%s_Sched" % (self.name)
    # get pool name for bacula file
    def get_pool_name(self):
        return "%s_Pool" % (self.name)

    def __unicode__(self):
        return self.name


### Schedule ###

class Schedule(models.Model):
    procedure = models.ForeignKey(Procedure)
    type = models.CharField(max_length=20,choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, default="Invalid")

    # change status to valid or invalid depending if get_trigger() returns the trigger of False
    def update_status(self):
        self.status = (self.get_trigger()) and 'Valid' or 'Invalid'
        self.save()

    # return the associated trigger or False in case of it doesnt exist
    def get_trigger(self):
        cmd = "trigger = %sTrigger.objects.get(schedule=self)" % (self.type)
        try:
            exec(cmd)
        except Exception, e: # DoesNotExist Exception means there's no trigger
            trigger = False
        return trigger
    
    def __unicode__(self):
        return self.procedure.name 


### WeeklyTrigger ###

class WeeklyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    for day in DAYS_OF_THE_WEEK:
        exec('%s = models.BooleanField()' % day)    
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)


### MonthlyTrigger ###

class MonthlyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)
    target_days = models.CharField(max_length=100)


### UniqueTrigger ###
class UniqueTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    target_date = models.DateField()
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)

### FileSet ###
class FileSet(models.Model):
    procedure = models.ForeignKey(Procedure)
    path = models.CharField(max_length="255")


### Pool ###
class Pool(models.Model):
    procedure = models.ForeignKey(Procedure)
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)
    
###
###   Signals
###
import backup_corporativo.bkp.signals
