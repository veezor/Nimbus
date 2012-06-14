#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Client(models.Model):
    clientid = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    uname = models.TextField()
    autoprune = models.IntegerField(null=True, blank=True)
    fileretention = models.BigIntegerField(null=True, blank=True)
    jobretention = models.BigIntegerField(null=True, blank=True)


    class Meta:
        db_table = u'client'
        verbose_name = _(u"Client")

    @property
    def computer(self):
        from nimbus.computers.models import Computer
        client_name = self.name.split('_')[0]
        return Computer.objects.get(uuid__uuid_hex=client_name)


class File(models.Model):
    fileid = models.BigIntegerField(primary_key=True)
    fileindex = models.IntegerField(null=True, blank=True)
    job = models.ForeignKey('Job', db_column='jobid')
    path = models.ForeignKey('Path', db_column='pathid')
    filename = models.ForeignKey('Filename', db_column='filenameid')
    markid = models.IntegerField(null=True, blank=True)
    lstat = models.TextField()
    md5 = models.TextField(blank=True)


    class Meta:
        db_table = u'file'
        verbose_name = _(u"File")


    @property
    def fullname(self):
        return self.path.path + self.filename.name


class Fileset(models.Model):
    filesetid = models.IntegerField(primary_key=True)
    fileset = models.TextField()
    md5 = models.TextField(blank=True)
    createtime = models.DateTimeField(null=True, blank=True)


    class Meta:
        db_table = u'fileset'
        verbose_name = _(u"Fileset")


class Filename(models.Model):
    filenameid = models.IntegerField(primary_key=True)
    name = models.TextField()


    class Meta:
        db_table = u'filename'
        verbose_name = _(u"Filename")

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
    STATUS_MESSAGES_MAPPING = {'C': (_(u'Created, not yet running'), 0),
                               'R': (_(u'Running'), 1),
                               'B': (_('uBlocked'), 2),
                               'T': (_('uCompleted successfully'),3),
                               'E': (_(u'Terminated with errors'),5),
                               'e': (_(u'Non-fatal error'),6),
                               'f': (_(u'Fatal error'),7),
                               'D': (_(u'Verify found differences'),8),
                               'A': (_(u'Canceled by user'),9),
                               'F': (_(u'Waiting for Client'),11),
                               'S': (_(u'Waiting for Storage daemon'),12),
                               'm': (_(u'Waiting for new media'),12),
                               'M': (_(u'Waiting for media mount'),12),
                               's': (_(u'Waiting for storage resource'),12),
                               'j': (_(u'Waiting for job resource'),12),
                               'c': (_(u'Waiting for client resource'),12),
                               'd': (_(u'Waiting on maximum jobs'),12),
                               't': (_(u'Waiting on start time'),12),
                               'p': (_(u'Waiting on higher priority jobs'),12),
                               'i': (_(u'Doing batch insert file records'),13),
                               'a': (_(u'SD despooling attributes'),12)}
    jobid = models.IntegerField(primary_key=True )
    job = models.TextField()
    name = models.TextField()
    type = models.CharField(max_length=1)
    level = models.CharField(max_length=1)
    client = models.ForeignKey(Client, null=True, blank=True, db_column='clientid')
    jobstatus = models.CharField(max_length=1)
    schedtime = models.DateTimeField(null=True, blank=True)
    starttime = models.DateTimeField(null=True, blank=True)
    endtime = models.DateTimeField(null=True, blank=True)
    realendtime = models.DateTimeField(null=True, blank=True)
    jobtdate = models.BigIntegerField(null=True, blank=True)
    volsessionid = models.IntegerField(null=True, blank=True)
    volsessiontime = models.IntegerField(null=True, blank=True)
    jobfiles = models.IntegerField(null=True, blank=True)
    jobbytes = models.BigIntegerField(null=True, blank=True)
    readbytes = models.BigIntegerField(null=True, blank=True)
    joberrors = models.IntegerField(null=True, blank=True)
    jobmissingfiles = models.IntegerField(null=True, blank=True)
    pool = models.ForeignKey('Pool', null=True, blank=True, db_column='poolid')
    fileset = models.ForeignKey('FileSet', null=True, blank=True, db_column='filesetid')
    priorjobid = models.IntegerField(null=True, blank=True)
    purgedfiles = models.IntegerField(null=True, blank=True)
    hasbase = models.IntegerField(null=True, blank=True)


    class Meta:
        db_table = u'job'
        verbose_name = _(u"Job")

    def __unicode__(self):
        return self.name

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
        status = 'undefined'

        if self.jobstatus in ['R', 'i', 'a']:
            status = 'running'
        elif self.jobstatus in ['F', 'S', 'm', 'M', 's', 'j', 'c', 'd', 't', 'p', 'C']:
            status = 'waiting'
        elif self.jobstatus in ['e', 'D']:
            status = 'warning'
        elif self.jobstatus in ['E','B', 'f','A']:
            status = 'error'
        else:
            status = 'ok'

        if status == 'ok' and self.joberrors> 0:
            status = 'warning'

        return status


    @property
    def human_general_status(self):
        return self.general_status

    @property
    def backup_level(self):
        if self.level == 'F':
            return 'Full'
        elif self.level == 'I':
            return 'Incremental'

    @property
    def backup_type(self):
        if self.type == "B":
            return 'Backup'
        elif self.type == 'R':
            return 'Restore'

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
        if self.type == "R":
            #Esta job nao tem um procedure definido pois eh um restore
            from nimbus.computers.models import Computer
            client_name = self.client.name.split('_')[0]
            fake_procedure = Procedure()
            fake_procedure.computer = Computer.objects.get(uuid__uuid_hex=client_name)
            return fake_procedure

        if not hasattr(self, '_procedure'):
            try:
                self._procedure = Procedure.objects.select_related().get(uuid__uuid_hex=procedure_name)
            except Procedure.DoesNotExist, error:
                self._procedure = None
        return self._procedure


    @property
    def status_message(self):
        #FIX-ME
        return self.STATUS_MESSAGES_MAPPING.get(self.jobstatus, _(u"Unknown"))[1]

    @property
    def duration(self):
        if self.endtime != None:
            return self.endtime - self.starttime
        else:
            datetime.now() - self.starttime



class JobMedia(models.Model):
    jobmediaid = models.IntegerField(primary_key=True)
    job = models.ForeignKey(Job, db_column='jobid')
    media = models.ForeignKey('Media', db_column='mediaid')
    firstindex = models.IntegerField(null=True, blank=True)
    lastindex = models.IntegerField(null=True, blank=True)
    startfile = models.IntegerField(null=True, blank=True)
    endfile = models.IntegerField(null=True, blank=True)
    startblock = models.IntegerField(null=True, blank=True)
    endblock = models.IntegerField(null=True, blank=True)
    volindex = models.IntegerField(null=True, blank=True)
    # copy = models.IntegerField(null=True, blank=True)
    # stripe = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'jobmedia'
        verbose_name = _(u"JobMedia")

class Media(models.Model):
    mediaid = models.IntegerField(primary_key=True)
    volumename = models.TextField(unique=True)
    slot = models.IntegerField(null=True, blank=True)
    pool = models.ForeignKey("Pool", null=True, blank=True, db_column='poolid')
    mediatype = models.TextField()
    mediatypeid = models.IntegerField(null=True, blank=True)
    labeltype = models.IntegerField(null=True, blank=True)
    firstwritten = models.DateTimeField(null=True, blank=True)
    lastwritten = models.DateTimeField(null=True, blank=True)
    labeldate = models.DateTimeField(null=True, blank=True)
    voljobs = models.IntegerField(null=True, blank=True)
    volfiles = models.IntegerField(null=True, blank=True)
    volblocks = models.IntegerField(null=True, blank=True)
    volmounts = models.IntegerField(null=True, blank=True)
    volbytes = models.BigIntegerField(null=True, blank=True)
    volparts = models.IntegerField(null=True, blank=True)
    volerrors = models.IntegerField(null=True, blank=True)
    volwrites = models.IntegerField(null=True, blank=True)
    volcapacitybytes = models.BigIntegerField(null=True, blank=True)
    volstatus = models.CharField(max_length=27)
    enabled = models.IntegerField(null=True, blank=True)
    recycle = models.IntegerField(null=True, blank=True)
    actiononpurge = models.IntegerField(null=True, blank=True)
    volretention = models.BigIntegerField(null=True, blank=True)
    voluseduration = models.BigIntegerField(null=True, blank=True)
    maxvoljobs = models.IntegerField(null=True, blank=True)
    maxvolfiles = models.IntegerField(null=True, blank=True)
    maxvolbytes = models.BigIntegerField(null=True, blank=True)
    inchanger = models.IntegerField(null=True, blank=True)
    storageid = models.IntegerField(null=True, blank=True)
    deviceid = models.IntegerField(null=True, blank=True)
    mediaaddressing = models.IntegerField(null=True, blank=True)
    volreadtime = models.BigIntegerField(null=True, blank=True)
    volwritetime = models.BigIntegerField(null=True, blank=True)
    endfile = models.IntegerField(null=True, blank=True)
    endblock = models.IntegerField(null=True, blank=True)
    locationid = models.IntegerField(null=True, blank=True)
    recyclecount = models.IntegerField(null=True, blank=True)
    initialwrite = models.DateTimeField(null=True, blank=True)
    scratchpoolid = models.IntegerField(null=True, blank=True)
    recyclepoolid = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    
    class Meta:
        db_table = u'media'
        verbose_name = _(u"JobMedia")


class Path(models.Model):
    pathid = models.IntegerField(primary_key=True)
    path = models.TextField()

    class Meta:
        db_table = u'path'
        verbose_name = _(u"Path")

class Pool(models.Model):
    poolid = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    numvols = models.IntegerField(null=True, blank=True)
    maxvols = models.IntegerField(null=True, blank=True)
    useonce = models.IntegerField(null=True, blank=True)
    usecatalog = models.IntegerField(null=True, blank=True)
    acceptanyvolume = models.IntegerField(null=True, blank=True)
    volretention = models.BigIntegerField(null=True, blank=True)
    voluseduration = models.BigIntegerField(null=True, blank=True)
    maxvoljobs = models.IntegerField(null=True, blank=True)
    maxvolfiles = models.IntegerField(null=True, blank=True)
    maxvolbytes = models.BigIntegerField(null=True, blank=True)
    autoprune = models.IntegerField(null=True, blank=True)
    recycle = models.IntegerField(null=True, blank=True)
    actiononpurge = models.IntegerField(null=True, blank=True)
    pooltype = models.CharField(max_length=27)
    labeltype = models.IntegerField(null=True, blank=True)
    labelformat = models.TextField(blank=True)
    enabled = models.IntegerField(null=True, blank=True)
    scratchpoolid = models.IntegerField(null=True, blank=True)
    recyclepoolid = models.IntegerField(null=True, blank=True)
    nextpoolid = models.IntegerField(null=True, blank=True)
    migrationhighbytes = models.BigIntegerField(null=True, blank=True)
    migrationlowbytes = models.BigIntegerField(null=True, blank=True)
    migrationtime = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'pool'
        verbose_name = _(u"Pool")


