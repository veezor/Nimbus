#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
from os import path
from os.path import join, exists

from django.utils.translation import ugettext as _
from django.db import models, connections
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, m2m_changed
from django.utils.translation import ugettext_lazy as _

from pybacula import BConsoleInitError

from nimbus.base.models import BaseModel
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.filesets.models import FileSet
from nimbus.schedules.models import Schedule
from nimbus.bacula.models import Media, Job, File
# from nimbus.pools.models import Pool
from nimbus.libs.template import render_to_file
from nimbus.libs.bacula import Bacula
from nimbus.shared import utils, enums, signals, fields

class GenericContentType(models.Model):

    @classmethod
    def on_remove(cls, procedure):
        pass


class JobTask(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True, blank=True, null=False)
    description = models.CharField(max_length=255)
    runsonclient = models.BooleanField(default=False, blank=True, null=False)
    runswhen = models.CharField(max_length=25, blank=False, null=False)
    command = models.CharField(max_length=1023, blank=False, null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=False, blank=False)
    creator = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        if self.active:
            return "%s - %s" % (self.name, self.description) 
        else:
            return " (off) %s - %s" % (self.name, self.description) 


class Procedure(BaseModel):
    pool_name = models.CharField(max_length=255)
    pool_size = models.BigIntegerField(blank=False, null=False, 
                                  default=settings.DEFAULT_PROCEDURE_POOL_SIZE,
                                  editable=False) #100MB
    pool_retention_time = models.IntegerField(verbose_name=_("Retention Time (days)"),
                                              blank=False, null=False,
                                              default=30)
    computer = models.ForeignKey(Computer, verbose_name=_("Computer"),
                                 blank=False, null=False)
    active = models.BooleanField(default=True, blank=True, null=False)
    schedule = models.ForeignKey(Schedule, verbose_name=_("Schedule"),
                                 related_name='procedures')
    fileset = models.ForeignKey(FileSet, verbose_name=_("Fileset"),
                                related_name='procedures')
    storage = models.ForeignKey(Storage, verbose_name=_("Storage device"), null=False,
                                blank=False)
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=False,
                            null=False)
    job_tasks = models.ManyToManyField(JobTask, verbose_name=_("Auxiliary tasks"),
                            related_name='procedure', blank=True, null=True)


    class Meta:
        verbose_name = _(u"Procedure")


    def fileset_bacula_name(self):
        return self.fileset.bacula_name
        # return self.profile.fileset.bacula_name
    
    def restore_bacula_name(self):
        return "%s_restorejob" % self.uuid.uuid_hex
        
    def schedule_bacula_name(self):
        return self.schedule.bacula_name
        # return self.profile.schedule.bacula_name

    def storage_bacula_name(self):
        return self.storage.bacula_name
        # return self.profile.storage.bacula_name

    def pool_bacula_name(self):
        return '%s_pool' % self.bacula_name

    def has_job_tasks(self, job_tasks_name):
        return self.job_tasks.get(name=job_tasks_name)

    @classmethod
    def jobs_with_job_tasks(cls, job_tasks_name):
        procedures = cls.objects.filter(job_tasks__name=job_tasks_name).exclude(id=1)
        job_names = [ p.bacula_name for p in procedures ]
        jobs = Job.objects.select_related().filter(name__in=job_names).order_by('-starttime')
        return jobs

    @classmethod
    def with_job_tasks(cls, job_tasks_name):
        procedures = cls.objects.filter(job_tasks__name=job_tasks_name).exclude(id=1)
        return procedures

    def last_success_date(self):
        return Job.objects.filter(name=self.bacula_name,jobstatus='T')\
                .order_by('-endtime')[0]

    @property
    def jobs_id_to_cancel(self):
        status = ('R','p','j','c','d','s','M','m','s','F','B', 'C') #TODO: refactor
        return Job.objects.filter(name=self.bacula_name,
                                  jobstatus__in=status).values_list('jobid', flat=True)

    @property
    def all_my_jobs(self):
        jobs = Job.objects.filter(name__startswith=self.bacula_name)
        return jobs

    @property
    def backup_jobs(self):
        return self.all_my_jobs.filter(type='B',jobstatus='T')


    @property
    def volume_names(self):
        pool_name = self.pool_bacula_name()
        medias = Media.objects.filter(pool__name=pool_name).distinct()
        return [m.volumename for m in medias]


    @property
    def all_my_good_jobs(self):
        jobs = Job.objects.filter(name__startswith=self.bacula_name, jobstatus="T").order_by('-starttime')
        return jobs
        
    @classmethod
    def all_jobs(cls):
        job_names = [ p.bacula_name for p in cls.objects.all() ]
        for name in job_names[:]:
            job_names.append(name+"restore")
        jobs = Job.objects.select_related().filter(name__in=job_names).order_by('-starttime')
        return jobs

    @classmethod
    def all_non_self_jobs(cls):
        job_names = [ p.bacula_name for p in cls.objects.exclude(id=1) ]
        for name in job_names[:]:
            job_names.append(name+"restore")
        # jobs = Job.objects.select_related().filter(name__in=job_names).order_by('-starttime')
        jobs = Job.objects.select_related().filter(Q(name__in=job_names) | Q(type="R") ).order_by('-starttime')
        return jobs

    def restore_jobs(self):
        return Job.objects.filter(client__name=self.computer.bacula_name,
                                  fileset__fileset=self.fileset_bacula_name,
                                  jobstatus='T').order_by('-endtime').distinct()[:15]

    def get_backup_jobs_between(self, start, end):
        jobs = Job.objects.filter(realendtime__range=(start,end), 
                                  jobfiles__gt=0, 
                                  jobstatus='T',
                                  type='B',
                                  name=self.bacula_name)\
                                                .order_by('-endtime').distinct()
        return jobs

    def __unicode__(self):
        return self.name 

    def run(self):
        bacula = Bacula()
        bacula.run_backup(self.bacula_name, 
                          client_name=self.computer.bacula_name)
   

    @staticmethod
    def list_files(jobid, computer, path="/"):
        if path == "":
            path = "/"
        bacula = Bacula()

        if computer.operation_system == "windows" and path == '/':
            files = File.objects.filter(job=jobid,
                                       path__path__isnull=False)\
                    .extra(select={'driver': 'substr( "path"."path", 0, 4)'})\
                    .values_list('driver', flat=True).distinct()
            return list(files)

        return bacula.list_files(jobid, path)



    @staticmethod
    def search_files(jobid, pattern):
        files = File.objects.filter(
                models.Q(filename__name__icontains=pattern) | models.Q(
                path__path__icontains=pattern), job__jobid=jobid).distinct()
        files = [f.fullname for f in files]
        files.sort()
        return files


    def cancel(self):
        bacula = Bacula()
        bacula.cancel_procedure(self)


    @classmethod
    def cancel_jobid(cls, job_id):
        bacula = Bacula()
        bacula.cancel_job(job_id)



def update_procedure_file(procedure):
    """Procedure update file"""
    name = procedure.bacula_name
    verbose_name = procedure.name
    filename = join(settings.NIMBUS_JOBS_DIR, name)
    render_to_file(filename,
                   "job",
                   name=name,
                   verbose_name=verbose_name,
                   schedule=procedure.schedule_bacula_name(),
                   storage=procedure.storage_bacula_name(),
                   fileset=procedure.fileset_bacula_name(),
                   priority="10",
                   active=procedure.active,
                   # NIMBUS_EXE=settings.NIMBUS_EXE,
                   client=procedure.computer.bacula_name,
                   pool=procedure.pool_bacula_name(),
                   job_tasks=procedure.job_tasks.filter(active=True),
                   )


    update_pool_file(procedure)

    if not exists(settings.NIMBUS_RESTORE_FILE):
        render_to_file(settings.NIMBUS_RESTORE_FILE,
                       "restore",
                       name=name + "restore",
                       storage=procedure.storage_bacula_name(),
                       fileset=procedure.fileset_bacula_name(),
                       client=procedure.computer.bacula_name,
                       pool=procedure.pool_bacula_name())


def remove_procedure_file(procedure):
    """remove procedure file"""
    base_dir,filepath = utils.mount_path(procedure.bacula_name,
                                         settings.NIMBUS_JOBS_DIR)
    utils.remove_or_leave(filepath)
    remove_pool_file(procedure)


def remove_procedure_volumes(procedure):
    pool_name = procedure.pool_bacula_name()
    medias = Media.objects.filter(pool__name=pool_name).distinct()
    volumes = [m.volumename for m in medias]
    try:
        bacula = Bacula()
        bacula.cancel_procedure(procedure)
        bacula.purge_volumes(volumes, pool_name)
        bacula.truncate_volumes(pool_name)
        bacula.delete_pool(pool_name)
        for volume in volumes:
            volume_abs_path = join(settings.NIMBUS_DEFAULT_ARCHIVE, volume)
            if exists(volume_abs_path):
                os.remove(volume_abs_path)


    except BConsoleInitError, error:
        logger = logging.getLogger(__name__)
        logger.exception(_("Error in communication with the Bacula"))



def update_pool_file(procedure):
    """Pool update pool bacula file"""
    name = procedure.pool_bacula_name()
    filename = path.join(settings.NIMBUS_POOLS_DIR, name)

    render_to_file(filename, "pool", name=name, max_vol_bytes=procedure.pool_size,
                   days=procedure.pool_retention_time)


def remove_pool_file(procedure):
    """pool remove file"""
    name = procedure.pool_bacula_name()
    filename = path.join(settings.NIMBUS_POOLS_DIR, name)
    utils.remove_or_leave(filename)

#signals.connect_on(update_pool_file, Procedure, post_save)
#signals.connect_on(remove_pool_file, Procedure, post_delete)

def pre_delete_procedure(procedure):
    #Execute on_remove de todos os job_tasks
    for r in procedure.job_tasks.all():
        if r.creator:
            r.creator.on_remove(procedure)

def change_job_tasks(sender, instance, action, reverse, model, pk_set, **kwargs):
    update_procedure_file(instance)

def update_job_tasks(job_tasks):
    procedures = Procedure.objects.filter(active=True)
    for procedure in procedures:
        if procedure.job_tasks.all():
            update_procedure_file(procedure)


m2m_changed.connect(change_job_tasks, sender=Procedure.job_tasks.through)
# signals.connect_on( offsiteconf_check, Procedure, pre_save)
signals.connect_on( update_procedure_file, Procedure, post_save)
signals.connect_on( update_job_tasks, JobTask, post_save)
signals.connect_on(pre_delete_procedure, Procedure, pre_delete)
signals.connect_on( remove_procedure_volumes, Procedure, post_delete)
signals.connect_on( remove_procedure_file, Procedure, post_delete)

