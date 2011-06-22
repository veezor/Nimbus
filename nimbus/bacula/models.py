#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from django.db import models

class Client(models.Model):
    clientid = models.IntegerField(primary_key=True, db_column='ClientId')
    name = models.TextField(unique=True, db_column='Name')
    uname = models.TextField(db_column='Uname')
    autoprune = models.IntegerField(null=True, db_column='AutoPrune', blank=True)
    fileretention = models.BigIntegerField(null=True, db_column='FileRetention', blank=True)
    jobretention = models.BigIntegerField(null=True, db_column='JobRetention', blank=True)
    class Meta:
        db_table = u'Client'

    @property
    def computer(self):
        from nimbus.computers.models import Computer
        client_name = self.name.split('_')[0]
        return Computer.objects.get(uuid__uuid_hex=client_name)


class File(models.Model):
    fileid = models.BigIntegerField(primary_key=True, db_column='FileId')
    fileindex = models.IntegerField(null=True, db_column='FileIndex', blank=True)
    job = models.ForeignKey('Job',db_column='JobId')
    path = models.ForeignKey('Path',db_column='PathId')
    filename = models.ForeignKey('Filename', db_column='FilenameId')
    markid = models.IntegerField(null=True, db_column='MarkId', blank=True)
    lstat = models.TextField(db_column='LStat')
    md5 = models.TextField(db_column='MD5', blank=True)
    class Meta:
        db_table = u'File'

    @property
    def fullname(self):
        return self.path.path + self.filename.name


class Fileset(models.Model):
    filesetid = models.IntegerField(primary_key=True, db_column='FileSetId')
    fileset = models.TextField(db_column='FileSet')
    md5 = models.TextField(db_column='MD5', blank=True)
    createtime = models.DateTimeField(null=True, db_column='CreateTime', blank=True)
    class Meta:
        db_table = u'FileSet'

class Filename(models.Model):
    filenameid = models.IntegerField(primary_key=True, db_column='FilenameId')
    name = models.TextField(db_column='Name')
    class Meta:
        db_table = u'Filename'

class Job(models.Model):
    MESSAGES = ['Criado mas sem executar ainda.',
                'Executando',
                'Bloqueado',
                'Terminado com sucesso',
                'Terminado com alertas',
                'Terminado com erros',
                'Erro nâo fatal',
                'Erro fatal',
                'Verificar diferenças',
                'Cancelado pelo usuário',
                'Incompleto',
                'Esperando pelo cliente',
                'Esperando',
                'Gravando dados']
    STATUS_MESSAGES_MAPPING = {'C': 'Created, not yet running',
                               'R': 'Running',
                               'B': 'Blocked',
                               'T': 'Completed successfully',
                               'E': 'Terminated with errors',
                               'e': 'Non-fatal error',
                               'f': 'Fatal error',
                               'D': 'Verify found differences',
                               'A': 'Canceled by user',
                               'F': 'Waiting for Client',
                               'S': 'Waiting for Storage daemon',
                               'm': 'Waiting for new media',
                               'M': 'Waiting for media mount',
                               's': 'Waiting for storage resource',
                               'j': 'Waiting for job resource',
                               'c': 'Waiting for client resource',
                               'd': 'Waiting on maximum jobs',
                               't': 'Waiting on start time',
                               'p': 'Waiting on higher priority jobs',
                               'i': 'Doing batch insert file records',
                               'a': 'SD despooling attributes'}
    jobid = models.IntegerField(primary_key=True, db_column='JobId')
    job = models.TextField(db_column='Job')
    name = models.TextField(db_column='Name')
    type = models.CharField(max_length=1, db_column='Type')
    level = models.CharField(max_length=1, db_column='Level')
    client = models.ForeignKey(Client, null=True, db_column='ClientId', blank=True)
    jobstatus = models.CharField(max_length=1, db_column='JobStatus')
    schedtime = models.DateTimeField(null=True, db_column='SchedTime', blank=True)
    starttime = models.DateTimeField(null=True, db_column='StartTime', blank=True)
    endtime = models.DateTimeField(null=True, db_column='EndTime', blank=True)
    realendtime = models.DateTimeField(null=True, db_column='RealEndTime', blank=True)
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True)
    volsessionid = models.IntegerField(null=True, db_column='VolSessionId', blank=True)
    volsessiontime = models.IntegerField(null=True, db_column='VolSessionTime', blank=True)
    jobfiles = models.IntegerField(null=True, db_column='JobFiles', blank=True)
    jobbytes = models.BigIntegerField(null=True, db_column='JobBytes', blank=True)
    readbytes = models.BigIntegerField(null=True, db_column='ReadBytes', blank=True)
    joberrors = models.IntegerField(null=True, db_column='JobErrors', blank=True)
    jobmissingfiles = models.IntegerField(null=True, db_column='JobMissingFiles', blank=True)
    pool = models.ForeignKey('Pool', null=True, db_column='PoolId', blank=True)
    fileset = models.ForeignKey('FileSet', null=True, db_column='FileSetId', blank=True)
    priorjobid = models.IntegerField(null=True, db_column='PriorJobId', blank=True)
    purgedfiles = models.IntegerField(null=True, db_column='PurgedFiles', blank=True)
    hasbase = models.IntegerField(null=True, db_column='HasBase', blank=True)

    @property
    def human_readable_size(self):
        size = float(self.jobbytes)
        if size > 1073741824:
            size = size/1073741824.0
            unit = 'GB'
        elif size > 1048576:
            size = size/1048576.0
            unit = 'MB'
        elif size > 1024:
            size = size/1024.0
            unit = 'KB'
        else:
            unit = 'B'
        return {'size': '%.2f' % size,
                'raw_size': size,
                'unit': unit}


    @property
    def general_status(self):
        if self.jobstatus in ['R', 'i', 'a']:
            return 'running'
        elif self.jobstatus in ['F', 'S', 'm', 'M', 's', 'j', 'c', 'd', 't', 'p']:
            return 'waiting'
        elif self.jobstatus in ['E', 'e', 'D', 'A']:
            return 'warning'
        elif self.jobstatus in ['B', 'f']:
            return 'error'
        else:
            return 'ok'

    @property
    def backup_level(self):
        if self.level == 'F':
            return 'Full'
        elif self.level == 'I':
            return 'Incremental'

    @property
    def end_time(self):
        return self.endtime.strftime('%H:%M:%S - %d/%m')

    @property
    def schedule_time(self):
        return self.schedtime.strftime('%H:%M - %d/%m')

    @property
    def start_time(self):
        return self.starttime.strftime('%H:%M:%S - %d/%m')

    @property
    def real_end_time(self):
        return self.realendtime.strftime('%H:%M:%S - %d/%m')


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
            nbytes =  bytes['total']  or 0
            result[day] = nbytes
        return result

    @property
    def procedure(self):
        from nimbus.procedures.models import Procedure
        procedure_name = self.name.split('_')[0]
        try:
            return Procedure.objects.get(uuid__uuid_hex=procedure_name)
        except:
            return None

    @property
    def status_friendly(self):
        if self.jobstatus == 'T':
            return 'ok'
        if self.jobstatus in ('e', 'E', 'f'):
            return 'error'
        if self.jobstatus == 'W':
            return 'warn'
        return 'running'

    @property
    def status_message(self):
        return self.STATUS_MESSAGES_MAPPING.get(self.jobstatus, "Desconhecido")

    @property
    def duration(self):
        if self.endtime != None:
            return self.endtime - self.starttime
        else:
            datetime.now() - self.starttime

    class Meta:
        db_table = u'Job'


class JobMedia(models.Model):
    jobmediaid = models.IntegerField(primary_key=True, db_column='JobMediaId')
    job = models.ForeignKey(Job, db_column='JobId')
    media = models.ForeignKey('Media', db_column='MediaId')
    firstindex = models.IntegerField(null=True, db_column='FirstIndex', blank=True)
    lastindex = models.IntegerField(null=True, db_column='LastIndex', blank=True)
    startfile = models.IntegerField(null=True, db_column='StartFile', blank=True)
    endfile = models.IntegerField(null=True, db_column='EndFile', blank=True)
    startblock = models.IntegerField(null=True, db_column='StartBlock', blank=True)
    endblock = models.IntegerField(null=True, db_column='EndBlock', blank=True)
    volindex = models.IntegerField(null=True, db_column='VolIndex', blank=True)
    copy = models.IntegerField(null=True, db_column='Copy', blank=True)
    stripe = models.IntegerField(null=True, db_column='Stripe', blank=True)
    class Meta:
        db_table = u'JobMedia'


class Media(models.Model):
    mediaid = models.IntegerField(primary_key=True, db_column='MediaId')
    volumename = models.TextField(unique=True, db_column='VolumeName')
    slot = models.IntegerField(null=True, db_column='Slot', blank=True)
    pool = models.ForeignKey("Pool", null=True, db_column='PoolId', blank=True)
    mediatype = models.TextField(db_column='MediaType')
    mediatypeid = models.IntegerField(null=True, db_column='MediaTypeId', blank=True)
    labeltype = models.IntegerField(null=True, db_column='LabelType', blank=True)
    firstwritten = models.DateTimeField(null=True, db_column='FirstWritten', blank=True)
    lastwritten = models.DateTimeField(null=True, db_column='LastWritten', blank=True)
    labeldate = models.DateTimeField(null=True, db_column='LabelDate', blank=True)
    voljobs = models.IntegerField(null=True, db_column='VolJobs', blank=True)
    volfiles = models.IntegerField(null=True, db_column='VolFiles', blank=True)
    volblocks = models.IntegerField(null=True, db_column='VolBlocks', blank=True)
    volmounts = models.IntegerField(null=True, db_column='VolMounts', blank=True)
    volbytes = models.BigIntegerField(null=True, db_column='VolBytes', blank=True)
    volparts = models.IntegerField(null=True, db_column='VolParts', blank=True)
    volerrors = models.IntegerField(null=True, db_column='VolErrors', blank=True)
    volwrites = models.IntegerField(null=True, db_column='VolWrites', blank=True)
    volcapacitybytes = models.BigIntegerField(null=True, db_column='VolCapacityBytes', blank=True)
    volstatus = models.CharField(max_length=27, db_column='VolStatus')
    enabled = models.IntegerField(null=True, db_column='Enabled', blank=True)
    recycle = models.IntegerField(null=True, db_column='Recycle', blank=True)
    actiononpurge = models.IntegerField(null=True, db_column='ActionOnPurge', blank=True)
    volretention = models.BigIntegerField(null=True, db_column='VolRetention', blank=True)
    voluseduration = models.BigIntegerField(null=True, db_column='VolUseDuration', blank=True)
    maxvoljobs = models.IntegerField(null=True, db_column='MaxVolJobs', blank=True)
    maxvolfiles = models.IntegerField(null=True, db_column='MaxVolFiles', blank=True)
    maxvolbytes = models.BigIntegerField(null=True, db_column='MaxVolBytes', blank=True)
    inchanger = models.IntegerField(null=True, db_column='InChanger', blank=True)
    storageid = models.IntegerField(null=True, db_column='StorageId', blank=True)
    deviceid = models.IntegerField(null=True, db_column='DeviceId', blank=True)
    mediaaddressing = models.IntegerField(null=True, db_column='MediaAddressing', blank=True)
    volreadtime = models.BigIntegerField(null=True, db_column='VolReadTime', blank=True)
    volwritetime = models.BigIntegerField(null=True, db_column='VolWriteTime', blank=True)
    endfile = models.IntegerField(null=True, db_column='EndFile', blank=True)
    endblock = models.IntegerField(null=True, db_column='EndBlock', blank=True)
    locationid = models.IntegerField(null=True, db_column='LocationId', blank=True)
    recyclecount = models.IntegerField(null=True, db_column='RecycleCount', blank=True)
    initialwrite = models.DateTimeField(null=True, db_column='InitialWrite', blank=True)
    scratchpoolid = models.IntegerField(null=True, db_column='ScratchPoolId', blank=True)
    recyclepoolid = models.IntegerField(null=True, db_column='RecyclePoolId', blank=True)
    comment = models.TextField(db_column='Comment', blank=True)
    class Meta:
        db_table = u'Media'


class Path(models.Model):
    pathid = models.IntegerField(primary_key=True, db_column='PathId')
    path = models.TextField(db_column='Path')
    class Meta:
        db_table = u'Path'


class Pool(models.Model):
    poolid = models.IntegerField(primary_key=True, db_column='PoolId')
    name = models.TextField(unique=True, db_column='Name')
    numvols = models.IntegerField(null=True, db_column='NumVols', blank=True)
    maxvols = models.IntegerField(null=True, db_column='MaxVols', blank=True)
    useonce = models.IntegerField(null=True, db_column='UseOnce', blank=True)
    usecatalog = models.IntegerField(null=True, db_column='UseCatalog', blank=True)
    acceptanyvolume = models.IntegerField(null=True, db_column='AcceptAnyVolume', blank=True)
    volretention = models.BigIntegerField(null=True, db_column='VolRetention', blank=True)
    voluseduration = models.BigIntegerField(null=True, db_column='VolUseDuration', blank=True)
    maxvoljobs = models.IntegerField(null=True, db_column='MaxVolJobs', blank=True)
    maxvolfiles = models.IntegerField(null=True, db_column='MaxVolFiles', blank=True)
    maxvolbytes = models.BigIntegerField(null=True, db_column='MaxVolBytes', blank=True)
    autoprune = models.IntegerField(null=True, db_column='AutoPrune', blank=True)
    recycle = models.IntegerField(null=True, db_column='Recycle', blank=True)
    actiononpurge = models.IntegerField(null=True, db_column='ActionOnPurge', blank=True)
    pooltype = models.CharField(max_length=27, db_column='PoolType')
    labeltype = models.IntegerField(null=True, db_column='LabelType', blank=True)
    labelformat = models.TextField(db_column='LabelFormat', blank=True)
    enabled = models.IntegerField(null=True, db_column='Enabled', blank=True)
    scratchpoolid = models.IntegerField(null=True, db_column='ScratchPoolId', blank=True)
    recyclepoolid = models.IntegerField(null=True, db_column='RecyclePoolId', blank=True)
    nextpoolid = models.IntegerField(null=True, db_column='NextPoolId', blank=True)
    migrationhighbytes = models.BigIntegerField(null=True, db_column='MigrationHighBytes', blank=True)
    migrationlowbytes = models.BigIntegerField(null=True, db_column='MigrationLowBytes', blank=True)
    migrationtime = models.BigIntegerField(null=True, db_column='MigrationTime', blank=True)
    class Meta:
        db_table = u'Pool'


# TODO: Dar um nome melhor a esta classe
class Temp(models.Model):
    jobid = models.ForeignKey(Job, db_column='JobId', primary_key=True)
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True)
    client = models.ForeignKey(Client, db_column='ClientId')
    level = models.CharField(max_length=3, db_column='Level')
    jobfiles = models.IntegerField(null=True, db_column='JobFiles', blank=True)
    jobbytes = models.BigIntegerField(null=True, db_column='JobBytes', blank=True)
    starttime = models.DateTimeField(null=True, db_column='StartTime', blank=True)
    volumename = models.CharField(max_length=384, db_column='VolumeName')
    startfile = models.IntegerField(null=True, db_column='StartFile', blank=True)
    volsessionid = models.IntegerField(null=True, db_column='VolSessionId', blank=True)
    volsessiontime = models.IntegerField(null=True, db_column='VolSessionTime', blank=True)
    class Meta:
        db_table = u'temp'


# TODO: Dar um nome melhor a esta classe também
class Temp1(models.Model):
    job = models.ForeignKey(Job, db_column='JobId', primary_key=True)
    jobtdate = models.BigIntegerField(null=True, db_column='JobTDate', blank=True)
    class Meta:
        db_table = u'temp1'