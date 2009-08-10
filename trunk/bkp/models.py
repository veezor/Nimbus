#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core import serializers
from django.db import models
from django import forms
from backup_corporativo.bkp import customfields as cfields
from backup_corporativo.bkp import utils
import os, string, time


### Constants ###
TYPE_CHOICES = (
    ('Weekly', 'Semanal'),
    ('Monthly', 'Mensal'),
)

LEVEL_CHOICES = (
    ('Full', 'Completo'),
    ('Incremental', 'Incremental'),
)

OS_CHOICES = (
    ('WIN', 'Windows'),
    ('UNIX', 'Unix'),
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
    server_ip = models.IPAddressField("Endereço IP")
    director_password = models.CharField(max_length=50,default='defaultpw')
    director_port = models.IntegerField("Porta do Director",default='9101')
    storage_port = models.IntegerField("Porta do Storage",default='9103')
    database_name = models.CharField(max_length=50, default='bacula')
    database_user = models.CharField(max_length=50, default='root')
    database_password = models.CharField(max_length=50)
    max_upload_bandwidth = models.CharField("Limite de Upload", max_length=15, default='100 mbps')
    admin_mail = models.EmailField("E-mail do Admin", max_length=50, blank=True)

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
    computer_ip = models.IPAddressField("Endereço IP")
    computer_so = models.CharField("Sistema Operacional",max_length=50,choices=OS_CHOICES)
    computer_encryption = models.BooleanField("Encriptar Dados?",default=False)
    computer_description = models.TextField("Descrição",max_length=100, blank=True)
    computer_password = models.CharField("Password",max_length=100, editable=False,default='defaultpw')
    bacula_id = models.IntegerField("Bacula ID", default=BACULA_VOID_ID)
    
    # TODO: replace fetchall for custom dictfetch
    def get_status(self):
        """Gets client lastjob status"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_STATUS_RAW_QUERY
        status_query = CLIENT_STATUS_RAW_QUERY % {'client_name':self.computer_name,}
        cursor = BaculaDatabase.execute(status_query)
        result = cursor.fetchone()
        status = result and result[0] or ''

        if status == 'T':
            return 'Ativo'
        elif status == 'E':
            return 'Erro'
        else:
            return 'Desconhecido'

    def computer_key(self):
        return "%s.key" % self.computer_name
    
    def computer_cert(self):
        return "%s.cert" % self.computer_name
        
    def computer_pem(self):
        return "%s.pem" % self.computer_name
    
    def computer_key_path(self):
        return utils.absolute_file_path(self.computer_key(),"custom/crypt/")

    def computer_cert_path(self):
        return utils.absolute_file_path(self.computer_cert(),"custom/crypt/")

    def computer_pem_path(self):
        return utils.absolute_file_path(self.computer_pem(),"custom/crypt/")

    def generate_rsa_key(self):
        """Generates client rsa key.
        The key is needed for certificate generation.
        Will only generate if it wasnt previously generated.
        """
        from backup_corporativo.bkp.crypt_utils import GENERATE_KEY_RAW_CMD
        crypt_path = utils.absolute_dir_path('custom/crypt')
        utils.create_or_leave(crypt_path)
        if not os.path.isfile(self.computer_key_path()):
            cmd = GENERATE_KEY_RAW_CMD %    {'out':self.computer_key_path(),}
            os.system(cmd)
    
    def generate_certificate(self):
        """Generates client certificate based on key.
        The certificate is needed for pem generation.
        Will only generate if it wasnt previously generated.
        """
        from backup_corporativo.bkp.crypt_utils import GENERATE_CERT_RAW_CMD
        crypt_path = utils.absolute_dir_path('custom/crypt')
        utils.create_or_leave(crypt_path)
        if not os.path.isfile(self.computer_key_path()):
            cmd = GENERATE_CERT_RAW_CMD %   {'key_path':self.computer_key_path(),
                                            'out':self.computer_cert_path(),}
            os.system(cmd)
    
    def dump_pem(self):
        """Generates client pem using providaded key and certificate"""
        from backup_corporativo.bkp.crypt_utils import GET_PEM_RAW_CMD
        if not os.path.isfile(self.computer_key_path()): self.generate_rsa_key()
        if not os.path.isfile(self.computer_cert_path()): self.generate_certificate()
        cmd = GET_PEM_RAW_CMD % {'key_path':self.computer_key_path(),
                                'cert_path':self.computer_cert_path(),}
        pem = os.popen(cmd).read()
        return pem
        
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
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_RUNNING_JOBS_RAW_QUERY
        running_jobs_query = CLIENT_RUNNING_JOBS_RAW_QUERY % {'client_name':self.computer_name,}
        running_jobs_cursor = BaculaDatabase.execute(running_jobs_query)
        return utils.dictfetch(running_jobs_cursor)

    def last_jobs(self):
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import CLIENT_LAST_JOBS_RAW_QUERY
        last_jobs_query = CLIENT_LAST_JOBS_RAW_QUERY % {'client_name':self.computer_name,}
        last_jobs_cursor = BaculaDatabase.execute(last_jobs_query)
        return utils.dictfetch(last_jobs_cursor)
        
    def run_test_job(self):
        """Sends an empty job running requisition to bacula for this computer"""
        from backup_corporativo.bkp.bacula import Bacula;
        Bacula.run_backup(JobName='empty job', client_name=self.computer_name)
        
    def get_computer_name(self):
        """Returns computer name lower string."""
        return str.lower(str(self.computer_name))
        
    def change_password(self):
        """Changes the password to a new random password."""
        self.__set_computer_password(size)
        self.save()

    def absolute_url(self):
        """Returns absolute url."""
        return "computer/%s" % (self.id)

    def view_url(self):
        """Returns absolute url."""
        return "computer/%s" % (self.id)

    def edit_url(self):
        """Returns absolute url."""
        return "computer/%s/edit" % (self.id)

    def delete_url(self):
        """Returns delete url."""
        return "computer/%s/delete" % (self.id)

    def config_dump_url(self):
        """Returns config dump url."""
        return "computer/%s/config_dump" % (self.id)

    def pem_dump_url(self):
        """Returns pem dump url."""
        return "computer/%s/pem_dump" % (self.id)

    def run_test_url(self):
        """Returns run test url."""
        return "computer/%s/test" % (self.id)

    def save(self):
        if not self.id: # If this record is not at database yet
            self.__set_computer_password()
            self.generate_rsa_key()
            self.generate_certificate()        
        super(Computer, self).save()
        if self.bacula_id == self.BACULA_VOID_ID:
            self.__update_bacula_id()
            
    def __update_bacula_id(self):
        """Queries bacula database for client id"""
        from backup_corporativo.bkp.sql_queries import CLIENT_ID_RAW_QUERY
        from backup_corporativo.bkp.bacula import BaculaDatabase
        
        cliend_id_query = CLIENT_ID_RAW_QUERY % {'client_name':self.get_computer_name()}
        cursor = BaculaDatabase.cursor()
        cursor.execute(cliend_id_query)
        client_id = cursor.fetchone()
        self.bacula_id = client_id and client_id[0] or self.BACULA_ERROR_ID
        self.save()
    
    
    def __set_computer_password(self, size=20):
        """Sets a new random password to the computer.
        Dont ever call self.save() inside this function otherwise it will cause infinite loop.
        """
        from backup_corporativo.bkp.utils import random_password
        self.computer_password = random_password(size)


    def __unicode__(self):
        return "%s (%s)" % (self.computer_name, self.computer_ip)



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
            self.__set_storage_password()
        super(Storage, self).save()

    def delete(self):
        if self.storage_name == 'StorageLocal':
            raise Exception('StorageLocal não pode ser removido.') # TODO: create custom NimbusException classes
        else:
            super(Storage, self).delete()
        
    def __set_storage_password(self, size=20):
        """Sets a new random password to the storage.
        Dont ever call self.save() inside this function otherwise it will cause infinite loop.
        """
        from backup_corporativo.bkp.utils import random_password
        self.storage_password = random_password(size)


    def absolute_url(self):
        """Returns absolute url."""
        return "storage/%s" % (self.id)

    def view_url(self):
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

    # ClassMethods
    def get_default_storage(cls):
        try:
            def_sto = cls.objects.get(storage_name='StorageLocal')
        except cls.DoesNotExist:
            def_sto = False
        return def_sto
    get_default_storage = classmethod(get_default_storage)

        
### Procedure ###
class Procedure(models.Model):
    computer = models.ForeignKey(Computer)
    procedure_name = cfields.ModelSlugField("Nome",max_length=50,unique=True)
    storage = models.ForeignKey(Storage, default=None)

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
        restore_jobs_query = CLIENT_RESTORE_JOBS_RAW_QUERY %   {'client_name':self.computer.computer_name, 
                                                        'file_set':self.get_fileset_name(),}
        cursor = BaculaDatabase.execute(restore_jobs_query)
        return utils.dictfetch(cursor)

    def get_bkp_dict(self, bkp_jid):
        """Returns a dict with job information of a given job id"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import JOB_INFO_RAW_QUERY
        starttime_query = JOB_INFO_RAW_QUERY %    {'job_id':bkp_jid,}
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
        if 'StartTime' in initial_bkp and 'Level' in initial_bkp and initial_bkp['Level'] == 'I':
            load_full_query = LOAD_LAST_FULL_RAW_QUERY %  {'client_id':self.computer.bacula_id,
                                                    'start_time':initial_bkp['StartTime'],
                                                    'fileset':self.get_fileset_name(),}
        elif 'JobId' in initial_bkp and 'Level' in initial_bkp and initial_bkp['Level'] == 'F':
            load_full_query = LOAD_FULL_RAW_QUERY % {'jid':initial_bkp['JobId']}
        #TODO refactore BaculaDatabase so we can commit through there.            
        b2 = BaculaDatabaseWrapper()
        cursor = b2.cursor()
        cursor.execute(load_full_query)
        b2.commit()

    def get_tdate(self):
        """Gets tdate from a 1-row-table called temp1 which holds last full backup when properly loaded."""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import TEMP1_TDATE_QUERY
        cursor = BaculaDatabase.execute(TEMP1_TDATE_QUERY)
        result = cursor.fetchone()
        return result and result[0] or ''


    def load_full_media(self):
        """
        Loads media information for lasfull backup at table called temp.
        for more information, see LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import BaculaDatabaseWrapper
        from backup_corporativo.bkp.sql_queries import LOAD_FULL_MEDIA_INFO_QUERY
        #TODO refactore BaculaDatabase so we can commit through there.            
        b2 = BaculaDatabaseWrapper()
        cursor = b2.cursor()
        cursor.execute(LOAD_FULL_MEDIA_INFO_QUERY)
        b2.commit()
        
    def load_inc_media(self,initial_bkp):
        """
        Loads media information for incremental backups at table called temp.
        for more information, see LOAD_FULL_MEDIA_INFO_RAW_QUERY at sql_queryes.py
        """
        from backup_corporativo.bkp.bacula import BaculaDatabaseWrapper
        from backup_corporativo.bkp.sql_queries import LOAD_INC_MEDIA_INFO_RAW_QUERY
        tdate = self.get_tdate()
        
        if 'StartTime' in initial_bkp:
            incmedia_query = LOAD_INC_MEDIA_INFO_RAW_QUERY %    {'tdate':tdate,
                                                                'start_time':initial_bkp['StartTime'],
                                                                'client_id':self.computer.bacula_id,
                                                                'fileset':self.get_fileset_name(),}
            #TODO refactore BaculaDatabase so we can commit through there.            
            b2 = BaculaDatabaseWrapper()
            cursor = b2.cursor()
            cursor.execute(incmedia_query)
            b2.commit()

    def load_backups_information(self,initial_bkp):
        self.load_full_bkp(initial_bkp)         # load full bkp general info into temp1
        self.load_full_media()                  # load full bkp media info into temp
        if 'Level' in initial_bkp and initial_bkp['Level'] == 'I':
            self.load_inc_media(initial_bkp)    # load inc bkps media info into temp
            

    def build_jid_list(self,bkp_jid):
        """
        If temp1 and temp tables are properly feeded, will build a list with all
        job ids included at this restore. For more information, see 
        JOBS_FOR_RESTORE_QUERY at sql_queries.py
        """
        from backup_corporativo.bkp.sql_queries import JOBS_FOR_RESTORE_QUERY
        from backup_corporativo.bkp.bacula import BaculaDatabase
        initial_bkp = self.get_bkp_dict(bkp_jid)
        jid_list = []
        if initial_bkp:
            self.load_backups_information(initial_bkp)  # loads full bkp info and inc bkps information if exists
            cursor = BaculaDatabase.execute(JOBS_FOR_RESTORE_QUERY)
            job_list = utils.dictfetch(cursor)

            for job in job_list:
                jid_list.append(str(job['JobId']))
        return jid_list

    def get_file_tree(self, bkp_jid):
        """Retrieves tree with files from a job id list"""
        from backup_corporativo.bkp.bacula import BaculaDatabase
        from backup_corporativo.bkp.sql_queries import FILE_TREE_RAW_QUERY
        jid_list = self.build_jid_list(bkp_jid)    # build list with all job ids
        if jid_list:
            filetree_query = FILE_TREE_RAW_QUERY %  {'jid_string_list':','.join(jid_list),}
            cursor = BaculaDatabase.execute(filetree_query)
            count = cursor.rowcount
            file_list = utils.dictfetch(cursor)
            return count,self.build_file_tree(file_list)
        else: return 0,[]
    
    def build_file_tree(self, file_list):
        """Build tree from file list"""
        import os
        files = []

        for f in file_list:
            files.append('%s:%s' % (os.path.join(f['FPath'], f['FName']), f['FId']))
        return utils.parse_filetree(files)
        
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
    path = cfields.ModelPathField("Diretório", max_length="255")

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

class NimbusLog(models.Model):
    entry_timestamp = models.DateTimeField(default='',blank=True)
    entry_category = models.CharField(max_length=30)
    entry_type = models.CharField(max_length=30)
    entry_content = models.TextField()
    
    def save(self):
        self.entry_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            from backup_corporativo.settings import LOG_LEVEL #TODO colocar LOG_LEVEL dentro de GlobalConfig
            if LOG_LEVEL == 0:          # Nenhum log
                pass
            elif LOG_LEVEL == 1:        # Somente em arquivo
                self.new_file_entry()
            elif LOG_LEVEL == 2:        # Somente em banco de dados
                super(NimbusLog, self).save()
            elif LOG_LEVEL == 3:        # Arquivo + banco de dados
                self.new_file_entry()
                super(NimbusLog, self).save()
            else:                       # LOG_LEVEL desconhecido
                raise Exception('Erro de configuração: LOG_LEVEL desconhecido.')
        except ImportError:
            pass

    def new_file_entry(self):
        nlog = NimbusLog.get_log_file()
        log_entry = "%s [%s] - %s: %s" % (self.entry_timestamp, self.entry_category, self.entry_type, self.entry_content)
        nlog.write(str(log_entry).encode("string-escape"))
        nlog.write("\n")
        nlog.close()

    # ClassMethods
    def get_log_file(cls):
        return utils.prepare_to_write('log_geral','custom/logs/',mod='a')
    get_log_file = classmethod(get_log_file)
    
    def notice(cls, category, type, content):
        n1 = NimbusLog()
        n1.entry_category = category
        n1.entry_type = type
        n1.entry_content = content
        n1.save()
    notice = classmethod(notice)
    

###
###   Signals
###
import backup_corporativo.bkp.signals
