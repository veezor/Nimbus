#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from django.core import serializers
from django.db import models
from django import forms
from django.db.models import Sum

from nimbus.shared import utils
import nimbus.shared.sqlqueries as sql 

from nimbus.base.models import BaseModel

from nimbus.lib.bacula import BaculaDatabase

from nimbus.computers.models import Computer


class Profile(models.Model):
    name = models.CharField(max_length=255 ,unique=True,
                            blank=True, null=False)
    storage = models.ForeignKey(Storage, null=False, blank=False)
    fileset = models.ForeignKey(FileSet, null=False, blank=False)
    schedule = models.ForeignKey(Schedule, null=False, blank=False)




class Procedure(BaseModel):
    computer = models.ForeignKey(Computer, blank=False, null=False)
    profile = models.ForeignKey(Profile, blank=False, null=False)
    offsite_on = models.BooleanField(default=False, blank=False, null=False)

    def fileset_bacula_name(self):
        return self.profile.fileset.bacula_name()
    
    def restore_bacula_name(self):
        return "%s_restorejob" % self.uuid.uuid_hex
        
    def schedule_bacula_name(self):
        return self.profile.schedule.bacula_name()

    def pool_bacula_name(self):
        pool = self.pool_set.get()
        return pool.bacula_name()



    def last_success_date(self):
        last_success_date_query = sql.LAST_SUCCESS_DATE_RAW_QUERY % {
            'procedure_name':self.procedure_bacula_name()
        }
        baculadb = BaculaDatabase()
        cursor = baculadb.execute(last_success_date_query)
        result = utils.dictfetch(cursor)
        return result and result[0] or {}


    def restore_jobs(self):
        restore_jobs_query = sql.CLIENT_RESTORE_JOBS_RAW_QUERY % {
            'client_name':self.computer.computer_bacula_name(), 
            'file_set':self.fileset_bacula_name(),
        }
        baculadb = BaculaDatabase()
        cursor = baculadb.execute(restore_jobs_query)
        return utils.dictfetch(cursor)

    def get_bkp_dict(self, bkp_jid):
        """Returns a dict with job information of a given job id"""
        starttime_query = sql.JOB_INFO_RAW_QUERY % {'job_id':bkp_jid,}
        baculadb = BaculaDatabase()
        cursor = baculadb.execute(starttime_query)
        result = utils.dictfetch(cursor)
        return result and result[0] or {}

  
    def clean_temp(self):
        """Drop temp and temp1 tables"""
        drop_temp_query = sql.DROP_TABLE_RAW_QUERY % {'table_name':'temp'}
        drop_temp1_query = sql.DROP_TABLE_RAW_QUERY % {'table_name':'temp1'}
        baculadb = BaculaDatabase()
        baculadb.execute(drop_temp_query)
        baculadb.execute(drop_temp1_query)
        baculadb.execute(sql.CREATE_TEMP_QUERY)
        baculadb.execute(sql.CREATE_TEMP1_QUERY)
        
    
    def load_full_bkp(self, initial_bkp):
        """
        Loads last full job id and startime at table called temp1.
        for more information, see CLIENT_LAST_FULL_RAW_QUERY at sql_queries.py
        """
        self.clean_temp()
        if ('StartTime' in initial_bkp and
            'Level' in initial_bkp
            and initial_bkp['Level'] == 'I'):
            load_full_query = sql.LOAD_LAST_FULL_RAW_QUERY % {
                'client_id':self.computer.bacula_id,
                'start_time':initial_bkp['StartTime'],
                'fileset':self.get_fileset_name(),}
        elif ('JobId' in initial_bkp
              and 'Level' in initial_bkp
              and initial_bkp['Level'] == 'F'):
            load_full_query = sql.LOAD_FULL_RAW_QUERY % {
                'jid':initial_bkp['JobId']}
        b2 = BaculaDatabase()
        cursor = b2.execute(load_full_query)
        b2.commit()

    def get_tdate(self):
        """Gets tdate from a 1-row-table called temp1 which
        holds last full backup when properly loaded.
        """
        b2 = BaculaDatabase()
        cursor = b2.execute(sql.TEMP1_TDATE_QUERY)
        result = cursor.fetchone()
        return result and result[0] or ''


    def load_full_media(self):
        """
        Loads media information for lasfull backup at table
        called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        b2 = BaculaDatabase()
        cursor = b2.execute(sql.LOAD_FULL_MEDIA_INFO_QUERY)
        b2.commit()
        
    def load_inc_media(self,initial_bkp):
        """
        Loads media information for incremental backups at
        table called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        tdate = self.get_tdate()
        
        if 'StartTime' in initial_bkp:
            incmedia_query = sql.LOAD_INC_MEDIA_INFO_RAW_QUERY % {
                'tdate':tdate,
                'start_time':initial_bkp['StartTime'],
                'client_id':self.computer.bacula_id,
                'fileset':self.get_fileset_name(),}
            b2 = BaculaDatabase()
            cursor = b2.execute(incmedia_query)
            b2.commit()

    def load_backups_information(self,initial_bkp):
        # load full bkp general info into temp1
        self.load_full_bkp(initial_bkp)
        # load full bkp media info into temp
        self.load_full_media() 
        if 'Level' in initial_bkp and initial_bkp['Level'] == 'I':
            # load inc bkps media info into temp
            self.load_inc_media(initial_bkp) 
            

    def build_jid_list(self,bkp_jid):
        """
        If temp1 and temp tables are properly feeded, will
        build a list with all job ids included at this restore.
        For more information, see 
        JOBS_FOR_RESTORE_QUERY at sqlqueries.py
        """
        initial_bkp = self.get_bkp_dict(bkp_jid)
        jid_list = []
        if initial_bkp:
            # loads full bkp info and inc bkps information if exists
            self.load_backups_information(initial_bkp)
            b2 = BaculaDatabase()
            cursor = b2.execute(sql.JOBS_FOR_RESTORE_QUERY)
            job_list = utils.dictfetch(cursor)

            for job in job_list:
                jid_list.append(str(job['JobId']))
        return jid_list

    def get_file_tree(self, bkp_jid):
        """Retrieves tree with files from a job id list"""
        # build list with all job ids
        jid_list = self.build_jid_list(bkp_jid)    
        if jid_list:
            filetree_query = sql.FILE_TREE_RAW_QUERY % {
                'jid_string_list':','.join(jid_list),}
            b2 = BaculaDatabase()
            cursor = b2.execute(filetree_query)
            count = cursor.rowcount
            file_list = utils.dictfetch(cursor)
            return count,self.build_file_tree(file_list)
        else: return 0,[]
    
    def build_file_tree(self, file_list):
        """Build tree from file list"""
        files = [
            '%s:%s' % (
                os.path.join(f['FPath'],
                f['FName']),
                f['FId']) \
            for f in file_list]
        return utils.parse_filetree(files)
        

    def __unicode__(self):
        return u"Procedure(profile=%s,computer=%s)" % ( self.profile,
                                                        self.computer )

    
    @classmethod
    def disable_offsite(cls):
        offsite_procedures = cls.objects.filter(offsite_on=True)
        for procedure in offsite_procedures:
            procedure.offsite_on = False
            procedure.save()

