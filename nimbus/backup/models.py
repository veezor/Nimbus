#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models
from nimbus.computers.models import Computer
from nimbus.schedules.models import BackupLevel, Schedule, Month, Week, Day, Hour

class FileSet(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)

class FilePath(models.Model):
    path = models.CharField(unique=True, null=False, max_length=255)
    fileset = models.ForeignKey(FileSet, null=False, blank=False)


# class BackupLevel(models.Model):
#     name = models.CharField(max_length=255, unique=True, null=False)
# 
#     def __unicode__(self):
#         return self.name
#         
# 
# class Schedule(models.Model):
#     name = models.CharField(u'Nome qualquer', max_length=255, null=False, blank=False)
# 
# 
# class Month(models.Model):
#     schedule = models.OneToOneField(Schedule)
#     days = models.CommaSeparatedIntegerField(null=False, max_length=255)
#     level = models.ForeignKey(BackupLevel)
#     hour = models.TimeField()
# 
# 
# class Week(models.Model):
#     schedule = models.OneToOneField(Schedule)
#     days = models.CommaSeparatedIntegerField(null=False, max_length=255)
#     level = models.OneToOneField(BackupLevel)
#     hour = models.TimeField()
# 
# 
# class Day(models.Model):
#     schedule = models.OneToOneField(Schedule)
#     level = models.ForeignKey(BackupLevel)
#     hour = models.TimeField()
# 
# 
# class Hour(models.Model):
#     schedule = models.OneToOneField(Schedule, related_name='hour_triggers')
#     level = models.ForeignKey(BackupLevel)
#     minute = models.PositiveSmallIntegerField()

class Storage(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)


class Pool(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    retention_time = models.IntegerField()


class Procedure(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    computer = models.ForeignKey(Computer, related_name="procedure_test_set")
    offsite_on = models.BooleanField()
    retention_time = models.CharField(max_length=255, unique=True, null=False, blank=False)
    schedule = models.ForeignKey(Schedule, related_name='schedule')
    fileset = models.ForeignKey(FileSet, related_name='fileset')