#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

from django.db import models
from nimbus.shared import utils




class Client(models.Model):
    clientid = models.IntegerField(primary_key=True, db_column='ClientId') # Field name made lowercase.
    name = models.TextField(unique=True, db_column='Name') # Field name made lowercase.
    uname = models.TextField(db_column='Uname') # Field name made lowercase.
    autoprune = models.IntegerField(null=True, db_column='AutoPrune', blank=True) # Field name made lowercase.
    fileretention = models.BigIntegerField(null=True, db_column='FileRetention', blank=True) # Field name made lowercase.
    jobretention = models.BigIntegerField(null=True, db_column='JobRetention', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Client'


    @property
    def computer(self):
        from nimbus.computers.models import Computer
        client_name = self.name.split('_')[0]
        return Computer.objects.get(uuid__uuid_hex=client_name)




class File(models.Model):
    fileid = models.BigIntegerField(primary_key=True, db_column='FileId') # Field name made lowercase.
    fileindex = models.IntegerField(null=True, db_column='FileIndex', blank=True) # Field name made lowercase.
    job = models.ForeignKey('Job',db_column='JobId') # Field name made lowercase.
    path = models.ForeignKey('Path',db_column='PathId') # Field name made lowercase.
    filename = models.ForeignKey('Filename', db_column='FilenameId') # Field name made lowercase.
    markid = models.IntegerField(null=True, db_column='MarkId', blank=True) # Field name made lowercase.
    lstat = models.TextField(db_column='LStat') # Field name made lowercase.
    md5 = models.TextField(db_column='MD5', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'File'

    @property
    def fullname(self):
        return self.path.path + self.filename.name



class Fileset(models.Model):
    filesetid = models.IntegerField(primary_key=True, db_column='FileSetId') # Field name made lowercase.
    fileset = models.TextField(db_column='FileSet') # Field name made lowercase.
    md5 = models.TextField(db_column='MD5', blank=True) # Field name made lowercase.
    createtime = models.DateTimeField(null=True, db_column='CreateTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'FileSet'

class Filename(models.Model):
    filenameid = models.IntegerField(primary_key=True, db_column='FilenameId') # Field name made lowercase.
    name = models.TextField(db_column='Name') # Field name made lowercase.
    class Meta:
        db_table = u'Filename'

class Job(models.Model):
    jobid = models.IntegerField(primary_key=True, db_column='JobId') # Field name made lowercase.
    job = models.TextField(db_column='Job') # Field name made lowercase.
    name = models.TextField(db_column='Name') # Field name made lowercase.
    type = models.CharField(max_length=1, db_column='Type') # Field name made lowercase.
    level = models.CharField(max_length=1, db_column='Level') # Field name made lowercase.
    client = models.ForeignKey(Client, null=True, db_column='ClientId', blank=True) # Field name made lowercase.
    jobstatus = models.CharField(max_length=1, db_column='JobStatus') # Field name made lowercase.
    schedtime = models.DateTimeField(null=True, db_column='SchedTime', blank=True) # Field name made lowercase.
    starttime = models.DateTimeField(null=True, db_column='StartTime', blank=True) # Field name made lowercase.
    endtime = models.DateTimeField(null=True, db_column='EndTime', blank=True) # Field name made lowercase.
    realendtime = models.DateTimeField(null=True, db_column='RealEndTime', blank=True) # Field name made lowercase.
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True) # Field name made lowercase.
    volsessionid = models.IntegerField(null=True, db_column='VolSessionId', blank=True) # Field name made lowercase.
    volsessiontime = models.IntegerField(null=True, db_column='VolSessionTime', blank=True) # Field name made lowercase.
    jobfiles = models.IntegerField(null=True, db_column='JobFiles', blank=True) # Field name made lowercase.
    jobbytes = models.BigIntegerField(null=True, db_column='JobBytes', blank=True) # Field name made lowercase.
    readbytes = models.BigIntegerField(null=True, db_column='ReadBytes', blank=True) # Field name made lowercase.
    joberrors = models.IntegerField(null=True, db_column='JobErrors', blank=True) # Field name made lowercase.
    jobmissingfiles = models.IntegerField(null=True, db_column='JobMissingFiles', blank=True) # Field name made lowercase.
    pool = models.ForeignKey('Pool', null=True, db_column='PoolId', blank=True) # Field name made lowercase.
    fileset = models.ForeignKey('FileSet', null=True, db_column='FileSetId', blank=True) # Field name made lowercase.
    priorjobid = models.IntegerField(null=True, db_column='PriorJobId', blank=True) # Field name made lowercase.
    purgedfiles = models.IntegerField(null=True, db_column='PurgedFiles', blank=True) # Field name made lowercase.
    hasbase = models.IntegerField(null=True, db_column='HasBase', blank=True) # Field name made lowercase.


    @classmethod
    def get_jobs_by_day(cls, date):
        return cls.objects.filter(realendtime__day = date.day,
                                  realendtime__month = date.month,
                                  realendtime__year = date.year,
                                  type='B')

    @classmethod
    def get_jobs_by_day_between(cls, start, end):

        diff = end - start
        days = diff.days
        oneday = timedelta(1)
        day = start
        count = 0

        result = []


        while count <= days:
            result.append( (day, cls.get_jobs_by_day(day)) )
            day = day + oneday
            count += 1

        return result


    @classmethod
    def get_jobs_from_last_seven_days(cls):

        now = datetime.now()
        start = now - timedelta(6)
        start = datetime(start.year, start.month, start.day)
        return cls.get_jobs_by_day_between(start, now)


    @classmethod
    def get_files_from_last_jobs(cls):
        jobs_by_day = cls.get_jobs_from_last_seven_days()
        result = {}

        for day, jobs in jobs_by_day:
            files = jobs.aggregate(total=models.Sum('jobfiles'))
            nfiles = files['total'] or 0
            result[day] = nfiles

        return result


    @classmethod
    def get_bytes_from_last_jobs(cls):
        jobs_by_day = cls.get_jobs_from_last_seven_days()

        result = {}

        for day, jobs in jobs_by_day:
            bytes = jobs.aggregate(total=models.Sum('jobbytes'))
            nbytes =  utils.bytes_to_mb( bytes['total']  or 0 )
            result[day] = nbytes


        return result



    @property
    def procedure(self):
        from nimbus.procedures.models import Procedure
        procedure_name = self.name.split('_')[0]
        return Procedure.objects.get(uuid__uuid_hex=procedure_name)


    @property
    def status_friendly(self):
        if self.jobstatus in ('T', 'W'):
            return 'ok'

        if self.jobstatus in ('e', 'E', 'f'):
            return 'error'

        return 'warn'





    @property
    def duration(self):
        if self.endtime != None:
            return self.endtime - self.starttime
        else:
            datetime.now() - self.starttime

    class Meta:
        db_table = u'Job'


class JobMedia(models.Model):
    jobmediaid = models.IntegerField(primary_key=True, db_column='JobMediaId') # Field name made lowercase.
    job = models.ForeignKey(Job, db_column='JobId') # Field name made lowercase.
    media = models.ForeignKey('Media', db_column='MediaId') # Field name made lowercase.
    firstindex = models.IntegerField(null=True, db_column='FirstIndex', blank=True) # Field name made lowercase.
    lastindex = models.IntegerField(null=True, db_column='LastIndex', blank=True) # Field name made lowercase.
    startfile = models.IntegerField(null=True, db_column='StartFile', blank=True) # Field name made lowercase.
    endfile = models.IntegerField(null=True, db_column='EndFile', blank=True) # Field name made lowercase.
    startblock = models.IntegerField(null=True, db_column='StartBlock', blank=True) # Field name made lowercase.
    endblock = models.IntegerField(null=True, db_column='EndBlock', blank=True) # Field name made lowercase.
    volindex = models.IntegerField(null=True, db_column='VolIndex', blank=True) # Field name made lowercase.
    copy = models.IntegerField(null=True, db_column='Copy', blank=True) # Field name made lowercase.
    stripe = models.IntegerField(null=True, db_column='Stripe', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'JobMedia'

class Media(models.Model):
    mediaid = models.IntegerField(primary_key=True, db_column='MediaId') # Field name made lowercase.
    volumename = models.TextField(unique=True, db_column='VolumeName') # Field name made lowercase.
    slot = models.IntegerField(null=True, db_column='Slot', blank=True) # Field name made lowercase.
    pool = models.ForeignKey("Pool", null=True, db_column='PoolId', blank=True) # Field name made lowercase.
    mediatype = models.TextField(db_column='MediaType') # Field name made lowercase.
    mediatypeid = models.IntegerField(null=True, db_column='MediaTypeId', blank=True) # Field name made lowercase.
    labeltype = models.IntegerField(null=True, db_column='LabelType', blank=True) # Field name made lowercase.
    firstwritten = models.DateTimeField(null=True, db_column='FirstWritten', blank=True) # Field name made lowercase.
    lastwritten = models.DateTimeField(null=True, db_column='LastWritten', blank=True) # Field name made lowercase.
    labeldate = models.DateTimeField(null=True, db_column='LabelDate', blank=True) # Field name made lowercase.
    voljobs = models.IntegerField(null=True, db_column='VolJobs', blank=True) # Field name made lowercase.
    volfiles = models.IntegerField(null=True, db_column='VolFiles', blank=True) # Field name made lowercase.
    volblocks = models.IntegerField(null=True, db_column='VolBlocks', blank=True) # Field name made lowercase.
    volmounts = models.IntegerField(null=True, db_column='VolMounts', blank=True) # Field name made lowercase.
    volbytes = models.BigIntegerField(null=True, db_column='VolBytes', blank=True) # Field name made lowercase.
    volparts = models.IntegerField(null=True, db_column='VolParts', blank=True) # Field name made lowercase.
    volerrors = models.IntegerField(null=True, db_column='VolErrors', blank=True) # Field name made lowercase.
    volwrites = models.IntegerField(null=True, db_column='VolWrites', blank=True) # Field name made lowercase.
    volcapacitybytes = models.BigIntegerField(null=True, db_column='VolCapacityBytes', blank=True) # Field name made lowercase.
    volstatus = models.CharField(max_length=27, db_column='VolStatus') # Field name made lowercase.
    enabled = models.IntegerField(null=True, db_column='Enabled', blank=True) # Field name made lowercase.
    recycle = models.IntegerField(null=True, db_column='Recycle', blank=True) # Field name made lowercase.
    actiononpurge = models.IntegerField(null=True, db_column='ActionOnPurge', blank=True) # Field name made lowercase.
    volretention = models.BigIntegerField(null=True, db_column='VolRetention', blank=True) # Field name made lowercase.
    voluseduration = models.BigIntegerField(null=True, db_column='VolUseDuration', blank=True) # Field name made lowercase.
    maxvoljobs = models.IntegerField(null=True, db_column='MaxVolJobs', blank=True) # Field name made lowercase.
    maxvolfiles = models.IntegerField(null=True, db_column='MaxVolFiles', blank=True) # Field name made lowercase.
    maxvolbytes = models.BigIntegerField(null=True, db_column='MaxVolBytes', blank=True) # Field name made lowercase.
    inchanger = models.IntegerField(null=True, db_column='InChanger', blank=True) # Field name made lowercase.
    storageid = models.IntegerField(null=True, db_column='StorageId', blank=True) # Field name made lowercase.
    deviceid = models.IntegerField(null=True, db_column='DeviceId', blank=True) # Field name made lowercase.
    mediaaddressing = models.IntegerField(null=True, db_column='MediaAddressing', blank=True) # Field name made lowercase.
    volreadtime = models.BigIntegerField(null=True, db_column='VolReadTime', blank=True) # Field name made lowercase.
    volwritetime = models.BigIntegerField(null=True, db_column='VolWriteTime', blank=True) # Field name made lowercase.
    endfile = models.IntegerField(null=True, db_column='EndFile', blank=True) # Field name made lowercase.
    endblock = models.IntegerField(null=True, db_column='EndBlock', blank=True) # Field name made lowercase.
    locationid = models.IntegerField(null=True, db_column='LocationId', blank=True) # Field name made lowercase.
    recyclecount = models.IntegerField(null=True, db_column='RecycleCount', blank=True) # Field name made lowercase.
    initialwrite = models.DateTimeField(null=True, db_column='InitialWrite', blank=True) # Field name made lowercase.
    scratchpoolid = models.IntegerField(null=True, db_column='ScratchPoolId', blank=True) # Field name made lowercase.
    recyclepoolid = models.IntegerField(null=True, db_column='RecyclePoolId', blank=True) # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Media'


class Path(models.Model):
    pathid = models.IntegerField(primary_key=True, db_column='PathId') # Field name made lowercase.
    path = models.TextField(db_column='Path') # Field name made lowercase.
    class Meta:
        db_table = u'Path'

class Pool(models.Model):
    poolid = models.IntegerField(primary_key=True, db_column='PoolId') # Field name made lowercase.
    name = models.TextField(unique=True, db_column='Name') # Field name made lowercase.
    numvols = models.IntegerField(null=True, db_column='NumVols', blank=True) # Field name made lowercase.
    maxvols = models.IntegerField(null=True, db_column='MaxVols', blank=True) # Field name made lowercase.
    useonce = models.IntegerField(null=True, db_column='UseOnce', blank=True) # Field name made lowercase.
    usecatalog = models.IntegerField(null=True, db_column='UseCatalog', blank=True) # Field name made lowercase.
    acceptanyvolume = models.IntegerField(null=True, db_column='AcceptAnyVolume', blank=True) # Field name made lowercase.
    volretention = models.BigIntegerField(null=True, db_column='VolRetention', blank=True) # Field name made lowercase.
    voluseduration = models.BigIntegerField(null=True, db_column='VolUseDuration', blank=True) # Field name made lowercase.
    maxvoljobs = models.IntegerField(null=True, db_column='MaxVolJobs', blank=True) # Field name made lowercase.
    maxvolfiles = models.IntegerField(null=True, db_column='MaxVolFiles', blank=True) # Field name made lowercase.
    maxvolbytes = models.BigIntegerField(null=True, db_column='MaxVolBytes', blank=True) # Field name made lowercase.
    autoprune = models.IntegerField(null=True, db_column='AutoPrune', blank=True) # Field name made lowercase.
    recycle = models.IntegerField(null=True, db_column='Recycle', blank=True) # Field name made lowercase.
    actiononpurge = models.IntegerField(null=True, db_column='ActionOnPurge', blank=True) # Field name made lowercase.
    pooltype = models.CharField(max_length=27, db_column='PoolType') # Field name made lowercase.
    labeltype = models.IntegerField(null=True, db_column='LabelType', blank=True) # Field name made lowercase.
    labelformat = models.TextField(db_column='LabelFormat', blank=True) # Field name made lowercase.
    enabled = models.IntegerField(null=True, db_column='Enabled', blank=True) # Field name made lowercase.
    scratchpoolid = models.IntegerField(null=True, db_column='ScratchPoolId', blank=True) # Field name made lowercase.
    recyclepoolid = models.IntegerField(null=True, db_column='RecyclePoolId', blank=True) # Field name made lowercase.
    nextpoolid = models.IntegerField(null=True, db_column='NextPoolId', blank=True) # Field name made lowercase.
    migrationhighbytes = models.BigIntegerField(null=True, db_column='MigrationHighBytes', blank=True) # Field name made lowercase.
    migrationlowbytes = models.BigIntegerField(null=True, db_column='MigrationLowBytes', blank=True) # Field name made lowercase.
    migrationtime = models.BigIntegerField(null=True, db_column='MigrationTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Pool'




class Temp(models.Model):
    jobid = models.ForeignKey(Job, db_column='JobId', primary_key=True) # Field name made lowercase.
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True) # Field name made lowercase.
    client = models.ForeignKey(Client, db_column='ClientId') # Field name made lowercase.
    level = models.CharField(max_length=3, db_column='Level') # Field name made lowercase.
    jobfiles = models.IntegerField(null=True, db_column='JobFiles', blank=True) # Field name made lowercase.
    jobbytes = models.BigIntegerField(null=True, db_column='JobBytes', blank=True) # Field name made lowercase.
    starttime = models.DateTimeField(null=True, db_column='StartTime', blank=True) # Field name made lowercase.
    volumename = models.CharField(max_length=384, db_column='VolumeName') # Field name made lowercase.
    startfile = models.IntegerField(null=True, db_column='StartFile', blank=True) # Field name made lowercase.
    volsessionid = models.IntegerField(null=True, db_column='VolSessionId', blank=True) # Field name made lowercase.
    volsessiontime = models.IntegerField(null=True, db_column='VolSessionTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'temp'

class Temp1(models.Model):
    job = models.ForeignKey(Job, db_column='JobId', primary_key=True) # Field name made lowercase.
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'temp1'

