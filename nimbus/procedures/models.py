#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
from os.path import join

from django.db import models, connections
from django.conf import settings
from django.db.models.signals import post_save, post_delete 

from nimbus.shared import utils, signals
import nimbus.shared.sqlqueries as sql 

from nimbus.base.models import BaseModel
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.filesets.models import FileSet
from nimbus.schedules.models import Schedule
from nimbus.pools.models import Pool
from nimbus.libs.template import render_to_file


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

    name = models.CharField(max_length=255, blank=False, null=False)
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
                .order_by('endtime')[0]


    def restore_jobs(self):
        return Job.objects.filter( client__name=self.computer.bacula_name,
                                   fileset__fileset=self.fileset_bacula_name,
                                   jobstatus='T').order_by('endtime').distinct()[:15]

    def get_job(self, id):
        """Returns job information of a given job id"""
        return Job.objects.get(jobid=bkp_jid)

  
    @classmethod
    def clean_temp(cls):
        """Drop temp and temp1 tables"""
        cursor = connections['bacula'].cursor()
        cursor.execute('delete from temp')
        cursor.execute('delete from temp1')
        
    
    def load_full_bkp(self, job):
        """
        Loads last full job id and startime at table called temp1.
        for more information, see CLIENT_LAST_FULL_RAW_QUERY at sql_queries.py
        """
        self.clean_temp()
        if job.level == 'I':
            load_full_query = sql.LOAD_LAST_FULL_RAW_QUERY % {
                                    'client_id': job.client.clientid,
                                    'start_time': job.starttime,
                                    'fileset':self.fileset_bacula_name()
            }
        elif  job.level == 'F':
            load_full_query = sql.LOAD_FULL_RAW_QUERY % {
                'jid': job.jobid}
        else:
            pass

        cursor = connections['bacula'].cursor()
        cursor.execute(load_full_query)
        cursor.commit()


    @classmethod
    def get_tdate(cls):
        """Gets tdate from a 1-row-table called temp1 which
        holds last full backup when properly loaded.
        """
        return Temp1.objects.all()[0]


    @classmethod
    def load_full_media(cls):
        """
        Loads media information for lasfull backup at table
        called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        cursor = connections['bacula'].cursor()
        cursor.execute(sql.LOAD_FULL_MEDIA_INFO_RAW_QUERY)
        cursor.commit()

        
    def load_inc_media(self, job):
        """
        Loads media information for incremental backups at
        table called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        tdate = self.get_tdate()
        
        if 'StartTime' in initial_bkp:
            incmedia_query = sql.LOAD_INC_MEDIA_INFO_RAW_QUERY % {
                'tdate': job.jobtdate,
                'start_time': job.starttime,
                'client_id': job.client.clientid,
                'fileset': self.fileset_bacula_name()
            }
            
            cursor = connections['bacula'].cursor()
            cursor.execute(incmedia_query)
            cursor.commit()

    def load_backups_information(self, job):
        # load full bkp general info into temp1
        self.load_full_bkp(job)
        # load full bkp media info into temp
        self.load_full_media() 
        if job.level == 'I':
            # load inc bkps media info into temp
            self.load_inc_media(initial_bkp) 
            

    def build_jid_list(self, jobid):
        """
        If temp1 and temp tables are properly feeded, will
        build a list with all job ids included at this restore.
        For more information, see 
        JOBS_FOR_RESTORE_QUERY at sqlqueries.py
        """
        job = self.get_job(jobid)

        if job:
            # loads full bkp info and inc bkps information if exists
            self.load_backups_information(job)
            jobs = Temp.objects.all().distinct().order_by('starttime').values('job_id')
            return [ job['job_id'] for job in jobs  ]  


    def get_file_tree(self, job_id):
        """Retrieves tree with files from a job id list"""
        # build list with all job ids
        ids = self.build_jid_list( job_ids )    
        files = File.objects.filter(job__jobid__in=ids)\
                .distinct()


    def get_backup_jobs_between(self, start, end):
        # jobs = Job.objects.filter(realendtime__range=(start,end), 
        #                           jobfiles__gt=0,
        #                           type='B',
        #                           name=self.bacula_name)\
        #         .distinct()
        jobs = Job.objects.filter(realendtime__range=(start,end), 
                                  jobfiles__gt=0,
                                  type='B')\
                .distinct()
        return jobs
    
        

    def __unicode__(self):
        return u"Procedure(profile=%s,computer=%s)" % ( self.profile,
                                                        self.computer )

    
    @classmethod
    def disable_offsite(cls):
        offsite_procedures = cls.objects.filter(offsite_on=True)
        for procedure in offsite_procedures:
            procedure.offsite_on = False
            procedure.save()


    @staticmethod
    def locate_files(jobid, path="/"):
        depth = utils.pathdepth(path)

        cursor = connections['bacula'].cursor()

        regex = r"^([a-zA-Z]:)?%s.*$" % path

        if path == "/": # get min depth files
            cursor.execute(sql.SELECT_MIN_FILES_DEPTH, params=(jobid,))
            depth = cursor.fetchone()[0]
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
                    offsite_param="-m %v",
                    pool=procedure.pool_bacula_name(),
                    client=procedure.computer.bacula_name,
                    poll=procedure.pool_bacula_name() )



def remove_procedure_file(procedure):
    """remove procedure file"""
    base_dir,filepath = utils.mount_path( procedure.bacula_name,
                                          settings.NIMBUS_JOBS_DIR)
    utils.remove_or_leave(filepath)
   


signals.connect_on( update_procedure_file, Procedure, post_save)
signals.connect_on( remove_procedure_file, Procedure, post_delete)
