#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
from os.path import join

from django.db import models, connections
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save 

from nimbus.shared import utils, signals, fields
import nimbus.shared.sqlqueries as sql 

from nimbus.base.models import BaseModel
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.filesets.models import FileSet
from nimbus.schedules.models import Schedule
from nimbus.pools.models import Pool
from nimbus.libs.template import render_to_file
from nimbus.libs.bacula import Bacula
from nimbus.offsite.models import Offsite


from nimbus.bacula.models import (Job, 
                                  Temp1, 
                                  JobMedia, 
                                  Temp,
                                  File)


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

 
    def get_file_tree(self, job_id):
        """Retrieves tree with files from a job id list"""
        # build list with all job ids
        ids = self.build_jid_list( job_id )    
        files = File.objects.filter(job__jobid__in=ids)\
                .distinct()


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
    def locate_files(jobid, path="/"):
        depth = utils.pathdepth(path)

        cursor = connections['bacula'].cursor()

        regex = r"^([a-zA-Z]:)?%s.*$" % path


        if path == "/": # get min depth files
            cursor.execute(sql.SELECT_MIN_FILES_DEPTH, params=(jobid,))
            depth = cursor.fetchone()[0]

            cursor.execute(sql.SELECT_FILES_FROM_JOB_PATH_DEPTH, 
                              params=(jobid, regex, depth))


            files = [ row[0] for row in cursor.fetchall() ]

            for filename in list(files):
                like = "%s%%"  % filename
                cursor.execute(sql.SELECT_NEXT_FILES_ON_DEPTH, params=(like, jobid,depth))
                nextdepth = cursor.fetchone()[0]

                cursor.execute(sql.SELECT_MORE_FILES_FROM_JOB_PATH_DEPTH, 
                                          params=(jobid, like, nextdepth))

                files.extend(  [ row[0] for row in cursor.fetchall() ]  )

        else:
            cursor.execute(sql.SELECT_NEXT_FILES_DEPTH, params=(jobid,depth))
            depth = cursor.fetchone()[0]

            cursor.execute(sql.SELECT_FILES_FROM_JOB_PATH_DEPTH, 
                                  params=(jobid, regex, depth))

            files = [ row[0] for row in cursor.fetchall() ]
            # files = [ (row[0], utils.get_filesize_from_lstat(row[1]))\
            #             for row in cursor.fetchall() ]
        return files


    @staticmethod
    def search_files(jobid, pattern):

        cursor = connections['bacula'].cursor()

        cursor.execute(sql.SELECT_FILES_FROM_PATTERN, 
                              params=(jobid, pattern))
                              
        files = [ row[0] for row in cursor.fetchall() ]
        # files = [ (row[0], utils.get_filesize_from_lstat(row[1]))\
        #             for row in cursor.fetchall() ]
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
                    offsite_param="--upload-requests %v",
                    client=procedure.computer.bacula_name,
                    pool=procedure.pool_bacula_name() )

    render_to_file( filename + "restore",
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

    base_dir,filepath = utils.mount_path( procedure.bacula_name + "restore",
                                          settings.NIMBUS_JOBS_DIR)
    utils.remove_or_leave(filepath)
   




def offsiteconf_check(procedure):
    offsite = Offsite.get_instance()
    if not offsite.active:
        procedure.offsite_on = False



signals.connect_on( offsiteconf_check, Procedure, pre_save)
signals.connect_on( update_procedure_file, Procedure, post_save)
signals.connect_on( remove_procedure_file, Procedure, post_delete)

