#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp.models import TYPE_CHOICES, LEVEL_CHOICES, OS_CHOICES, DAYS_OF_THE_WEEK
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time

from backup_corporativo.bkp.app_models.nimbus_uuid import NimbusUUID
from backup_corporativo.bkp.app_models.computer import Computer
from backup_corporativo.bkp.app_models.storage import Storage

### Procedure ###
class Procedure(models.Model):
    nimbus_uuid = models.ForeignKey(NimbusUUID)
    computer = models.ForeignKey(Computer)
    storage = models.ForeignKey(Storage)
    procedure_name = models.CharField(
        "Nome",
        max_length=50,unique=True)
    offsite_on = models.BooleanField(
        "Enviar para offsite?",
        default=False)
    pool_size = models.IntegerField(
        "Tamanho total ocupado (MB)",
        default=2048)
    retention_time = models.IntegerField(
        "Tempo de renteção (dias)",
        default=30)

    # Classe Meta é necessária para resolver um problema gerado quando se
    # declara um model fora do arquivo models.py. Foi utilizada uma solução
    # temporária que aparentemente funciona normalmente. 
    # Para mais informações sobre esse hack, acessar ticket:
    # http://code.djangoproject.com/ticket/4470
    # NOTA: No momento em que esse código foi escrito, o Django estava
    # na versão "Django-1.0.2-final" e uma alteração no core do Django
    # estava sendo discutida em paralelo, mas o ticket ainda encontrava-se em
    # aberto e portanto ainda sem solução definitiva.
    # Caso um dia a aplicação venha a quebrar nesse trecho do código por conta
    # de uma atualização para uma versão do Django superior a 1.0.2,
    # vale a pena verificar se alguma alteração foi realmente realizada
    # nessa nova versão do Django.
    # Para mais informações sobre essa correção, acessar ticket:
    # http://code.djangoproject.com/ticket/3591
    class Meta:
        app_label = 'bkp'    

    def save(self):
        NimbusUUID.generate_uuid_or_leave(self)
        super(Procedure, self).save()

    def procedure_bacula_name(self):
        return "%s_job" % self.nimbus_uuid.uuid_hex

    def fileset_bacula_name(self):
        return "%s_fileset" % self.nimbus_uuid.uuid_hex
    
    def restore_bacula_name(self):
        return "%s_restorejob" % self.nimbus_uuid.uuid_hex
        
    def schedule_bacula_name(self):
        return "%s_schedule" % self.nimbus_uuid.uuid_hex

    def pool_bacula_name(self):
        return "%s_pool" % self.nimbus_uuid.uuid_hex

    def build_backup(self, fset, sched, trigg):
        """Saves child objects in correct order."""
        fset.procedure = sched.procedure = self
        fset.save()
        sched.save()
        trigg.schedule = sched
        trigg.save()

    def restore_jobs(self):
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_RESTORE_JOBS_RAW_QUERY
        restore_jobs_query = CLIENT_RESTORE_JOBS_RAW_QUERY % {
            'client_name':self.computer.computer_bacula_name(), 
            'file_set':self.fileset_bacula_name(),}
        cursor = BaculaDatabase.execute(restore_jobs_query)
        return utils.dictfetch(cursor)

    def get_bkp_dict(self, bkp_jid):
        """Returns a dict with job information of a given job id"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import JOB_INFO_RAW_QUERY
        starttime_query = JOB_INFO_RAW_QUERY % {'job_id':bkp_jid,}
        cursor = BaculaDatabase.execute(starttime_query)
        result = utils.dictfetch(cursor)
        return result and result[0] or {}

  
    def clean_temp(self):
        """Drop temp and temp1 tables"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import DROP_TABLE_RAW_QUERY, CREATE_TEMP_QUERY, CREATE_TEMP1_QUERY
        drop_temp_query = DROP_TABLE_RAW_QUERY % {'table_name':'temp'}
        drop_temp1_query = DROP_TABLE_RAW_QUERY % {'table_name':'temp1'}
        BaculaDatabase.execute(drop_temp_query)
        BaculaDatabase.execute(drop_temp1_query)
        BaculaDatabase.execute(CREATE_TEMP_QUERY)
        BaculaDatabase.execute(CREATE_TEMP1_QUERY)
        
    
    def load_full_bkp(self, initial_bkp):
        """
        Loads last full job id and startime at table called temp1.
        for more information, see CLIENT_LAST_FULL_RAW_QUERY at sql_queries.py
        """
        from backup_corporativo.bkp.bacula import BaculaDatabaseWrapper
        from backup_corporativo.bkp.sql_queries import LOAD_LAST_FULL_RAW_QUERY
        from backup_corporativo.bkp.sql_queries import LOAD_FULL_RAW_QUERY
        self.clean_temp()
        if ('StartTime' in initial_bkp and
            'Level' in initial_bkp
            and initial_bkp['Level'] == 'I'):
            load_full_query = LOAD_LAST_FULL_RAW_QUERY % {
                'client_id':self.computer.bacula_id,
                'start_time':initial_bkp['StartTime'],
                'fileset':self.get_fileset_name(),}
        elif ('JobId' in initial_bkp
              and 'Level' in initial_bkp
              and initial_bkp['Level'] == 'F'):
            load_full_query = LOAD_FULL_RAW_QUERY % {
                'jid':initial_bkp['JobId']}
        b2 = BaculaDatabaseWrapper()
        cursor = b2.cursor()
        cursor.execute(load_full_query)
        b2.commit()

    def get_tdate(self):
        """Gets tdate from a 1-row-table called temp1 which
        holds last full backup when properly loaded.
        """
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import TEMP1_TDATE_QUERY
        cursor = BaculaDatabase.execute(TEMP1_TDATE_QUERY)
        result = cursor.fetchone()
        return result and result[0] or ''


    def load_full_media(self):
        """
        Loads media information for lasfull backup at table
        called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import BaculaDatabaseWrapper
        from backup_corporativo.bkp.sql_queries import LOAD_FULL_MEDIA_INFO_QUERY
        b2 = BaculaDatabaseWrapper()
        cursor = b2.cursor()
        cursor.execute(LOAD_FULL_MEDIA_INFO_QUERY)
        b2.commit()
        
    def load_inc_media(self,initial_bkp):
        """
        Loads media information for incremental backups at
        table called temp. For more information, see
        LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import BaculaDatabaseWrapper
        from backup_corporativo.bkp.sql_queries import LOAD_INC_MEDIA_INFO_RAW_QUERY
        tdate = self.get_tdate()
        
        if 'StartTime' in initial_bkp:
            incmedia_query = LOAD_INC_MEDIA_INFO_RAW_QUERY % {
                'tdate':tdate,
                'start_time':initial_bkp['StartTime'],
                'client_id':self.computer.bacula_id,
                'fileset':self.get_fileset_name(),}
            b2 = BaculaDatabaseWrapper()
            cursor = b2.cursor()
            cursor.execute(incmedia_query)
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
        JOBS_FOR_RESTORE_QUERY at sql_queries.py
        """
        from backup_corporativo.bkp.sql_queries import JOBS_FOR_RESTORE_QUERY
        from backup_corporativo.bkp.bacula import BaculaDatabase
        initial_bkp = self.get_bkp_dict(bkp_jid)
        jid_list = []
        if initial_bkp:
            # loads full bkp info and inc bkps information if exists
            self.load_backups_information(initial_bkp)
            cursor = BaculaDatabase.execute(JOBS_FOR_RESTORE_QUERY)
            job_list = utils.dictfetch(cursor)

            for job in job_list:
                jid_list.append(str(job['JobId']))
        return jid_list

    def get_file_tree(self, bkp_jid):
        """Retrieves tree with files from a job id list"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import FILE_TREE_RAW_QUERY
        # build list with all job ids
        jid_list = self.build_jid_list(bkp_jid)    
        if jid_list:
            filetree_query = FILE_TREE_RAW_QUERY % {
                'jid_string_list':','.join(jid_list),}
            cursor = BaculaDatabase.execute(filetree_query)
            count = cursor.rowcount
            file_list = utils.dictfetch(cursor)
            return count,self.build_file_tree(file_list)
        else: return 0,[]
    
    def build_file_tree(self, file_list):
        """Build tree from file list"""
        import os
        files = [
            '%s:%s' % (
                os.path.join(f['FPath'],
                f['FName']),
                f['FId']) \
            for f in file_list]
        return utils.parse_filetree(files)
        

    def edit_url(self):
        """Returns edit url."""
        return "procedure/%s/edit" % self.id
    
    def update_url(self):
        """Returns edit url."""
        return "procedure/%s/update" % self.id

    def delete_url(self):
        """Returns delete url."""
        return "procedure/%s/delete" % self.id

    def __unicode__(self):
        return self.procedure_name

#ClassMethods
    def disable_offsite(cls):
        offsite_procedures = cls.objects.filter(offsite_on=True)
        for proc in offsite_procedures:
            proc.offsite_on = False
            proc.save()
    disable_offsite = classmethod(disable_offsite)
