#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from os.path import join, exists

from django.db import models, connections
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save 

from nimbus.shared import utils, signals, fields


from pybacula import BConsoleInitError

from nimbus.base.models import BaseModel
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.filesets.models import FileSet
from nimbus.schedules.models import Schedule
from nimbus.bacula.models import Media
from nimbus.pools.models import Pool
from nimbus.libs.template import render_to_file
from nimbus.libs.bacula import Bacula
from nimbus.offsite.models import Offsite
from nimbus.libs import offsite



from nimbus.bacula.models import Job, File


class Profile(models.Model):
    name = models.CharField(max_length=255 ,unique=True,
                            blank=True, null=False)
    storage = models.ForeignKey(Storage, null=False, blank=False)
    fileset = models.ForeignKey(FileSet, null=False, blank=False)
    schedule = models.ForeignKey(Schedule, null=False, blank=False)

    def __unicode__(self):
        return self.name




class Procedure(BaseModel):

    name = models.CharField(max_length=255, blank=False, null=False,
                            validators=[fields.check_model_name])
    computer = models.ForeignKey(Computer, blank=False, null=False)
    profile = models.ForeignKey(Profile, blank=False, null=False)
    pool = models.ForeignKey(Pool, blank=False, null=False, editable=False)
    offsite_on = models.BooleanField(default=False, blank=False, null=False)
    active = models.BooleanField(default=True, blank=False, null=False, editable=False)

    def fileset_bacula_name(self):
        return self.profile.fileset.bacula_name
    
    def restore_bacula_name(self):
        return "%s_restorejob" % self.uuid.uuid_hex
        
    def schedule_bacula_name(self):
        return self.profile.schedule.bacula_name

    def storage_bacula_name(self):
        return self.profile.storage.bacula_name

    def pool_bacula_name(self):
        return self.pool.bacula_name


    def last_success_date(self):
        return Job.objects.filter(name=self.bacula_name,jobstatus='T')\
                .order_by('-endtime')[0]


    def restore_jobs(self):
        return Job.objects.filter( client__name=self.computer.bacula_name,
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
        bacula.run_backup(  self.bacula_name, 
                            client_name=self.computer.bacula_name)
   

    @classmethod
    def disable_offsite(cls):
        cls.objects.filter(offsite_on=True).update(offsite_on=False)


    @staticmethod
    def list_files(jobid, path="/"):
       bacula = Bacula()
       return bacula.list_files(jobid, path)


    @staticmethod
    def search_files(jobid, pattern):
        files = File.objects.filter(
                models.Q(filename__name__icontains=pattern) | models.Q(path__path__icontains=pattern),
                job__jobid=jobid
        ).distinct()
        files = [ f.fullname for f in files ]
        files.sort()
        return files



def update_procedure_file(procedure):
    """Procedure update file"""

    name = procedure.bacula_name

    filename = join(settings.NIMBUS_JOBS_DIR, name)

    render_to_file( filename,
                    "job",
                    name=name,
                    schedule=procedure.schedule_bacula_name(),
                    storage=procedure.storage_bacula_name(),
                    fileset=procedure.fileset_bacula_name(),
                    priority="10",
                    offsite=procedure.offsite_on,
                    active=procedure.active,
                    offsite_param="--upload-requests %v",
                    client=procedure.computer.bacula_name,
                    pool=procedure.pool_bacula_name() )

    if not exists(settings.NIMBUS_RESTORE_FILE):

        render_to_file( settings.NIMBUS_RESTORE_FILE,
                        "restore",
                        name=name + "restore",
                        storage=procedure.storage_bacula_name(),
                        fileset=procedure.fileset_bacula_name(),
                        client=procedure.computer.bacula_name,
                        pool=procedure.pool_bacula_name() )


def remove_procedure_file(procedure):
    """remove procedure file"""
    base_dir,filepath = utils.mount_path( procedure.bacula_name,
                                          settings.NIMBUS_JOBS_DIR)
    utils.remove_or_leave(filepath)


   


def remove_procedure_volumes(procedure):

    pool_name = procedure.pool_bacula_name()
    medias = Media.objects.filter(pool__name=pool_name).distinct()
    volumes = [ m.volumename for m in medias ]

    try:
        bacula = Bacula()
        bacula.purge_volumes(volumes, pool_name)
        bacula.truncate_volumes(pool_name)
        bacula.delete_pool(pool_name)
    except BConsoleInitError, error:
        logger = logging.getLogger(__name__)
        logger.exception("Erro na comunicação com o bacula")


    procedure.pool.delete()

    if procedure.offsite_on:

        remote_manager = offsite.RemoteManager()
        remote_manager.create_deletes_request( volumes )





def offsiteconf_check(procedure):
    offsite = Offsite.get_instance()
    if not offsite.active:
        procedure.offsite_on = False



signals.connect_on( offsiteconf_check, Procedure, pre_save)
signals.connect_on( update_procedure_file, Procedure, post_save)
signals.connect_on( remove_procedure_file, Procedure, post_delete)
signals.connect_on( remove_procedure_volumes, Procedure, post_delete)

