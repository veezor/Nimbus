#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp import customfields as cfields
import os
import string

### Constants ###
TYPE_CHOICES = (
    ('Weekly', 'Semanal'),
    ('Monthly', 'Mensal'),
)

LEVEL_CHOICES = (
    ('Full', 'Completo'),
    ('Incremental', 'Incremental'),
)

DAYS_OF_THE_WEEK = {
    'sunday':'Domingo','monday':'Segunda','tuesday':'Terça',
    'wednesday':'Quarta','thursday':'Quinta','friday':'Sexta',
    'saturday':'Sábado',
}

###
###   Models
###


### GlobalConfig ###
class GlobalConfig(models.Model):
    bacula_name = cfields.ModelSlugField("Nome da Instância", max_length=50)
    storage_ip = models.IPAddressField("IP do Servidor")
    storage_password = models.CharField(max_length=50,default='defaultpw')
    storage_port = models.IntegerField("Porta do Storage",default='9103')
    director_port = models.IntegerField("Porta do Director",default='9101')
    director_password = models.CharField(max_length=50,default='defaultpw')
    database_name = models.CharField(max_length=50, default='bacula')    
    database_user = models.CharField(max_length=50, default='root')
    database_password = models.CharField(max_length=50)
    admin_mail = models.EmailField("E-mail do Admin", max_length=50, blank=True)
    max_upload_bandwidth = models.CharField("Limite de Upload", max_length=15, default='100 mbps')

    def generate_passwords(self):
        """Generates random passwords."""
        from backup_corporativo.bkp.utils import random_password
        self.storage_password = random_password(50)
        self.director_password = random_password(50)

    def system_configured(self):
        """Returns True if system is configured, False otherwise."""
        return GlobalConfig.objects.all().count() > 0

    def save(self):
        if not self.id:
            self.generate_passwords()
        self.id = 1 # always use the same row id at database to store the config
        super(GlobalConfig, self).save()

 
### Computer ###
class Computer(models.Model):
    # Constants
    DEFAULT_LOCATION="/tmp/bacula-restore"
    BACULA_VOID_ID = -1
    BACULA_ERROR_ID = 0
    # Attributes
    computer_name = cfields.ModelSlugField("Nome",max_length=50,unique=True)
    ip = models.IPAddressField("Endereço IP")
    description = models.CharField("Descrição",max_length=100, blank=True)
    fd_password = models.CharField("Password",max_length=100, editable=False,default='defaultpw')
    bacula_id = models.IntegerField("Bacula ID", default=BACULA_VOID_ID) 
    
    # TODO: replace fetchall for custom dictfetch
    def get_status(self):
        """Gets client lastjob status"""
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import CLIENT_STATUS_RAW_QUERY
        status_query = CLIENT_STATUS_RAW_QUERY % {'client_name':self.computer_name,}
        cursor = Bacula.db_query(status_query)
        result = cursor.fetchall()
        status = result and result[0][0] or ''

        if status == 'T':
            return 'Ativo'
        elif status == 'E':
            return 'Erro'
        else:
            return 'Desconhecido'

    def build_backup(self, proc, fset, sched, wtrigg):
        """Saves child objects in correct order."""
        proc.computer = self
        proc.save()
        fset.procedure = sched.procedure = proc
        fset.save()
        sched.save()
        wtrigg.schedule = sched
        wtrigg.save()

    def running_jobs(self):
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import CLIENT_RUNNING_JOBS_RAW_QUERY
        running_jobs_query = CLIENT_RUNNING_JOBS_RAW_QUERY % {'client_name':self.computer_name,}
        running_jobs = Bacula.dictfetch_query(running_jobs_query)
        return running_jobs

    def last_jobs(self):
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import CLIENT_LAST_JOBS_RAW_QUERY
        last_jobs_query = CLIENT_LAST_JOBS_RAW_QUERY % {'client_name':self.computer_name,}
        last_jobs = Bacula.dictfetch_query(last_jobs_query)
        return last_jobs
        
    def run_test_job(self):
        """Sends an empty job running requisition to bacula for this computer"""
        from backup_corporativo.bkp.bacula import Bacula;
        Bacula.run_backup(JobName='empty job', client_name=self.computer_name)
        
    def get_computer_name(self):
        """Returns computer name lower string."""
        return str.lower(str(self.computer_name))
        
    def change_password(self, size):
        """Changes the password to a new random password."""
        self.__generate_password(size)
        self.save()

    def absolute_url(self):
        """Returns absolute url."""
        return "computer/%s" % (self.id)

    def edit_url(self):
        """Returns absolute url."""
        return "computer/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/delete" % (self.id)

    def run_test_url(self):
        """Returns run test url."""
        return "computer/%s/test" % (self.id)

    def save(self):
        if not self.id: # If this record is not at database yet
            self.__generate_password()
        super(Computer, self).save()
        if self.bacula_id == self.BACULA_VOID_ID:
            self.__update_bacula_id()
            
    def __update_bacula_id(self):
        """Queries bacula database for client id"""
        from backup_corporativo.bkp.sql_queries import CLIENT_ID_RAW_QUERY
        from backup_corporativo.bkp.bacula import Bacula
        
        cliend_id_query = CLIENT_ID_RAW_QUERY % {'client_name':self.get_computer_name()}
        client_id_dict = Bacula.dictfetch_query(cliend_id_query)
        self.bacula_id = client_id_dict and client_id_dict[0]['ClientId'] or self.BACULA_ERROR_ID
        self.save()
    
    
    def __generate_password(self, size=20):
        """Sets a new random password to the computer."""
        from backup_corporativo.bkp.utils import random_password
        self.fd_password = random_password(size)


    def __unicode__(self):
        return "%s (%s)" % (self.computer_name, self.ip)



### Storage ###
class Storage(models.Model):
    storage_name = cfields.ModelSlugField("Nome", max_length=50, unique=True)
    storage_ip = models.IPAddressField("Endereço IP")
    storage_port = models.IntegerField("Porta do Storage", default='9103')
    storage_password = models.CharField(max_length=50, default='defaultpw')
    
    storage_description = models.CharField("Descrição", max_length=100, blank=True)


    def get_storage_name(self):
        """Returns storage name lower string."""
        return str.lower(str(self.storage_name))


    def save(self):
        if not self.id: # If this record is not at database yet
            self.__generate_password()
        super(Storage, self).save()


    def __generate_password(self, size=20):
        """Sets a new random password to the computer."""
        from backup_corporativo.bkp.utils import random_password
        self.storage_password = random_password(size)


    def absolute_url(self):
        """Returns absolute url."""
        return "storage/%s" % (self.id)

    def edit_url(self):
        """Returns absolute url."""
        return "storage/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "storage/%s/delete" % (self.id)

    def __unicode__(self):
        return "%s (%s:%s)" % (self.storage_name, self.storage_ip, self.storage_port)


        
### Procedure ###
class Procedure(models.Model):
    computer = models.ForeignKey(Computer)
    storage = models.ForeignKey(Storage, default=None)
    
    procedure_name = cfields.ModelSlugField("Nome",max_length=50,unique=True)
    status = models.CharField(max_length=10, default="Invalid")

    def build_backup(self, fset, sched, trigg):
        """Saves child objects in correct order."""
        fset.procedure = sched.procedure = self
        fset.save()
        sched.save()
        trigg.schedule = sched
        trigg.save()

    def restore_jobs(self):
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import CLIENT_RESTORE_JOBS_RAW_QUERY
        restore_jobs_query = CLIENT_RESTORE_JOBS_RAW_QUERY %   {'client_name':self.computer.computer_name, 
                                                        'file_set':self.get_fileset_name(),}
        return Bacula.dictfetch_query(restore_jobs_query)

    def get_bkp_dict(self, bkp_jid):
        """Returns a dict with job information of a given job id"""
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import JOB_INFO_RAW_QUERY
        starttime_query = JOB_INFO_RAW_QUERY %    {'job_id':bkp_jid,}
        result = Bacula.dictfetch_query(starttime_query)
        return result and result[0] or {}

  
    def clean_temp(self):
        """Drop temp and temp1 tables"""
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import DROP_TABLE_RAW_QUERY, CREATE_TEMP_QUERY, CREATE_TEMP1_QUERY
        drop_temp_query = DROP_TABLE_RAW_QUERY % {'table_name':'temp'}
        drop_temp1_query = DROP_TABLE_RAW_QUERY % {'table_name':'temp1'}
        Bacula.db_query(drop_temp_query)
        Bacula.db_query(drop_temp1_query)
        Bacula.db_query(CREATE_TEMP_QUERY)
        Bacula.db_query(CREATE_TEMP1_QUERY)
        
    
    def load_full_bkp(self, last_inc_bkp):
        """
        Loads last full job id and startime at table called temp1.
        for more information, see CLIENT_LAST_FULL_RAW_QUERY at sql_queries.py
        """
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import LOAD_LAST_FULL_RAW_QUERY
        self.clean_temp()
        if 'StartTime' in last_inc_bkp:
            lastfull_query = LOAD_LAST_FULL_RAW_QUERY %  {'client_id':self.computer.bacula_id,
                                                    'start_time':last_inc_bkp['StartTime'],
                                                    'fileset':self.get_fileset_name(),}
            Bacula.db_query(lastfull_query)

    def get_tdate(self):
        """Gets tdate from a 1-row-table called temp1 which holds last full backup when properly loaded."""
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import TEMP1_TDATE_QUERY
        tdate_dict = Bacula.dictfetch_query(TEMP1_TDATE_QUERY)
        return tdate_dict and tdate_dict[0]['JobTDate'] or ''


    def load_full_media(self):
        """
        Loads media information for lasfull backup at table called temp.
        for more information, see LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import LOAD_FULL_MEDIA_INFO_QUERY
        Bacula.db_query(LOAD_FULL_MEDIA_INFO_QUERY)
        
    def load_inc_media(self,last_inc_bkp):
        """
        Loads media information for incremental backups at table called temp.
        for more information, see LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import LOAD_INC_MEDIA_INFO_RAW_QUERY
        tdate = self.get_tdate()
        
        if 'StartTime' in last_inc_bkp:
            incmedia_query = LOAD_INC_MEDIA_INFO_RAW_QUERY %    {'tdate':tdate,
                                                                'start_time':last_inc_bkp['StartTime'],
                                                                'client_id':self.computer.bacula_id,
                                                                'fileset':self.get_fileset_name(),
                                                                }
            Bacula.db_query(incmedia_query)

    def build_jid_list(self):
        """
        If temp1 and temp tables are properly feeded, will build a list with all
        job ids included at this restore. For more information, see 
        JOBS_FOR_RESTORE_QUERY at sql_queries.py
        """
        from backup_corporativo.bkp.sql_queries import JOBS_FOR_RESTORE_QUERY
        from backup_corporativo.bkp.bacula import Bacula
        result_list = Bacula.dictfetch_query(JOBS_FOR_RESTORE_QUERY)
        jid_list = []

        for item in result_list:
            jid_list.append(str(item['JobId']))
        return jid_list

    def get_file_tree(self, last_inc_bkp_jid):
        """Retrieves tree with files from a job id list"""
        from backup_corporativo.bkp.bacula import Bacula
        from backup_corporativo.bkp.sql_queries import FILE_TREE_RAW_QUERY
        last_inc_bkp = self.get_bkp_dict(last_inc_bkp_jid)
        self.load_full_bkp(last_inc_bkp)    # find last full backup
        self.load_full_media()              # load infos for full backup
        self.load_inc_media(last_inc_bkp)   # load infos for incremental backups
        jid_list = self.build_jid_list()    # build list with all job ids
        if jid_list:
            filetree_query = FILE_TREE_RAW_QUERY %  {'jid_string_list':','.join(jid_list),}
            file_tree = Bacula.dictfetch_query(filetree_query)
            return file_tree 
        else: return []
    
    def get_fileset_name(self):
        """Get fileset name for bacula file."""
        return "%s_Set" % (self.procedure_name)
        
    def get_procedure_name(self):
        """Get procedure name for bacula file."""
        return "%s_Job" % (self.procedure_name)
    
    def get_restore_name(self):
        """Get restore procedure name for bacula."""
        return "%s_RestoreJob" % (self.procedure_name)
        
    def get_schedule_name(self):
        """Get schedule name for bacula file."""
        return "%s_Sched" % (self.procedure_name)

    def get_pool_name(self):
        """Get pool name for bacula file."""
        return "%s_Pool" % (self.procedure_name)

    def edit_url(self):
        """Returns edit url."""
        return "computer/%s/procedure/%s/edit" % (self.computer_id, self.id)
    
    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/procedure/%s/delete" % (self.computer_id, self.id)

    def new_run_url(self):
        """Returns run url."""
        return "computer/%s/procedure/%s/run/new" % (self.computer_id, self.id)

    def create_run_url(self):
        """Returns run url."""
        return "computer/%s/procedure/%s/run/" % (self.computer_id, self.id)

    def __unicode__(self):
        return self.procedure_name


### Schedule ###
class Schedule(models.Model):
    procedure = models.ForeignKey(Procedure)
    type = models.CharField("Tipo",max_length=20,choices=TYPE_CHOICES)

    def get_trigger(self):
        """Returns the associated trigger or False in case of it doesnt exist."""
        cmd = "trigger = %sTrigger.objects.get(schedule=self)" % (self.type)
        try:
            exec(cmd)
        except Exception, e: # DoesNotExist Exception means there's no trigger
            trigger = False
            #raise Exception("Agendamento inválido, não possui detalhes.")
        return trigger

    def build_backup(self, trigg):
        """Saves child objects in correct order."""
        trigg.schedule = self
        trigg.save()

    def __unicode__(self):
        if self.type == "Weekly":
            return "Semanal"
        elif self.type == "Monthly":
            return "Mensal"

    def add_url(self):
        """Returns add url."""
        return "computer/%s/procedure/%s/schedule/" % (
                self.procedure.computer_id, self.procedure_id)

    def edit_url(self):
        """Returns edit url."""
        return "computer/%s/procedure/%s/schedule/%s/edit" % (
                self.procedure.computer_id, self.procedure_id, self.id)

    def update_url(self):
        """Returns edit url."""
        return "computer/%s/procedure/%s/schedule/%s/update" % (
                self.procedure.computer_id, self.procedure_id, self.id)

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/procedure/%s/schedule/%s/delete" % (
                self.procedure.computer_id, self.procedure_id, self.id)


### WeeklyTrigger ###
class WeeklyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    for day in DAYS_OF_THE_WEEK.keys():
        exec('''%s = models.BooleanField("%s")''' % (day,DAYS_OF_THE_WEEK[day]))    
    hour = models.TimeField("Horário")
    level = models.CharField("Nível", max_length=20,choices=LEVEL_CHOICES)


### MonthlyTrigger ###
class MonthlyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    hour = models.TimeField("Horário")
    level = models.CharField("Nível", max_length=20,choices=LEVEL_CHOICES)
    target_days = cfields.ModelMonthDaysListField("Dias do Mês", max_length=100)
    
    def save(self):
        self.__sanitize_target_days()
        super(MonthlyTrigger,self).save()
        
    def __sanitize_target_days(self):
        """Removes duplicated day entries"""
        s = set(self.target_days.split(';'))
        self.target_days = ";".join(sorted(list(s)))

### FileSet ###
class FileSet(models.Model):
    procedure = models.ForeignKey(Procedure)
    path = cfields.ModelPathField("Local", max_length="255")

    def add_url(self):
        """Returns add url."""
        return "computer/%s/procedure/%s/fileset/" % (
                self.procedure.computer_id, self.procedure_id)

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/procedure/%s/fileset/%s/delete" % (
                self.procedure.computer_id, self.procedure_id, self.id)

    def __unicode__(self):
        return self.path


### Pool ###
class Pool(models.Model):
    # pools are created when Procedure is created through signals
    procedure = models.ForeignKey(Procedure)
    
### External Device ###
class ExternalDevice(models.Model):
    device_name = models.CharField("Nome",max_length=20)
    uuid = models.CharField("Dispositivo", max_length=50, unique=True)
    mount_index = models.IntegerField(unique=True)

    def mount_cmd(self):
        """Returns unix mount command"""
        return '''mount UUID=%s /mnt/%s''' % (self.uuid, self.mount_index)

    def __unicode__(self):
        return "%s (UUID %s)" % (self.device_name,self.uuid)

    def edit_url(self):
        """Returns edit url."""
        return "device/%s/edit" % (self.id)

    def update_url(self):
        """Returns edit url."""
        return "device/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "device/%s/delete" % (self.id)


    # ClassMethods
    def device_choices(cls):
        dev_choices = []
        import os
        import re
        label_re = '''LABEL="(?P<label>.*?)"'''
        uuid_re = '''UUID="(?P<uuid>.*?)"'''
        cmd = 'blkid'
        output = os.popen(cmd).read()
        lines = output.split('\n')
    
        for line in lines:
            label = uuid = None
            label_se = re.search(label_re, line)
            uuid_se = re.search(uuid_re, line)
    
            if label_se:
                label = label_se.group('label')
            if uuid_se:
                uuid = uuid_se.group('uuid')
            if label and uuid:
                dev_choices.append([uuid,label])
       
        return dev_choices
    device_choices = classmethod(device_choices)

    #TODO: improve next piece of code
    def next_device_index(cls):
        import MySQLdb
        from backup_corporativo.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_HOST
        query = "select max(mount_index) from bkp_externaldevice;"
        max_index = False
        try:
            db = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, passwd=DATABASE_PASSWORD, db=DATABASE_NAME)
            cursor = db.cursor()
            cursor.execute(query)
            max_index = cursor.fetchall()[0][0]+1
        except:
            pass
        return max_index and max_index or 0
    next_device_index = classmethod(next_device_index)
   

### Day of the Week
class DayOfTheWeek(models.Model):
    day_name = models.CharField("Name",max_length=10)

    def __unicode__(self):
		return self.day_name

### Restriction Time
class RestrictionTime(models.Model):
    restriction_time = models.TimeField("Hora")

    def __unicode__(self):
		return '%s' % self.restriction_time

### Bandwidth Restriction ###
class BandwidthRestriction(models.Model):
    dayoftheweek = models.ForeignKey(DayOfTheWeek)
    restrictiontime = models.ForeignKey(RestrictionTime)
    restriction_value = models.IntegerField("Restrição")

    def delete_url(self):
        return "restriction/%s/delete" % (self.id)

    def __unicode__(self):
        day = DAYS_OF_THE_WEEK[self.dayoftheweek.day_name]
        return '%shs %s %s kbps' % (self.restrictiontime,self.dayoftheweek,self.restriction_value)


###
###   Signals
###
import backup_corporativo.bkp.signals
