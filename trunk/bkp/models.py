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
    database_password = models.CharField(max_length=50, default='defaultpw')
    admin_mail = models.EmailField("E-mail do Admin", max_length=50, blank=True)
    max_upload_bandwidth = models.CharField("Limite de Upload", max_length=15, default='100 mbps')

    def generate_passwords(self):
        """Generates random passwords."""
        from backup_corporativo.bkp.utils import random_password
        self.storage_password = random_password(50)
        self.director_password = random_password(50)
        self.database_password = random_password(50)

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
    computer_name = cfields.ModelSlugField("Nome",max_length=50,unique=True)
    ip = models.IPAddressField("Endereço IP")
    description = models.CharField("Descrição",max_length=100, blank=True)
    fd_password = models.CharField("Password",max_length=100, editable=False,default='defaultpw')
    DEFAULT_LOCATION="/tmp/bacula-restore"
    
    def build_backup(self, proc, fset, sched, wtrigg):
        """Saves child objects in correct order."""

        proc.computer = self
        proc.save()
        
        fset.procedure = sched.procedure = proc
        fset.save()
        sched.save()
        
        wtrigg.schedule = sched
        wtrigg.save()
 
    def run_job(self, jobid):
        import os

    def run_test_job(self, client_source, job_id):
        """Run testjob for test communication between bacula's dir and client's fd.
        client_source: is the client that needs to be tested
        jobid: a jobid of the testjob
        """
        #TODO validates existance of client_name and client_restore
        cmd = "bconsole << BACULAEOF \n%s%sBACULAEOF" % (client_source, job_id)
        os.system(cmd)


    def run_restore_job(self, client_source, client_restore, job_id, where=DEFAULT_LOCATION):
        """Run restore for retrieve last backups for a given client.
        client_source: is the client owner of the files
        client_restore: is the client that will hold the restored files
        where: is the folder in client_restore that files will be restored
        jobid: a jobid or a comma separated list of jobids
        """
        #TODO validates existance of client_name and client_restore
        cmd = "bconsole << BACULAEOF \nrestore client=%s restoreclient=%s select all done yes where=%s jobid=%s \n12\nBACULAEOF" % (client_source, client_restore, where, job_id)
        os.system(cmd)
  

    def procedures_list(self):
        """Gets list of associated procedure."""
        return Procedure.objects.filter(computer=self.id)

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

    def save(self):
        if not self.id: # If this record is not at database yet
            self.__generate_password()
        super(Computer, self).save()
    
    
    def __generate_password(self, size=20):
        """Sets a new random password to the computer."""
        from backup_corporativo.bkp.utils import random_password
        self.fd_password = random_password(size)


    def __unicode__(self):
        return self.computer_name
        
### Procedure ###
# TODO remove list definitions and replace it for default <child>_set definition
class Procedure(models.Model):
    computer = models.ForeignKey(Computer)
    procedure_name = cfields.ModelSlugField("Nome",max_length=50,unique=True)
    status = models.CharField(max_length=10, default="Invalid")

    def build_backup(self, fset, sched, trigg):
        """Saves child objects in correct order."""

        fset.procedure = sched.procedure = self
        fset.save()
        sched.save()
        trigg.schedule = sched
        trigg.save()

    def update_status(self):
        """Change status to valid or invalid depending if filesets_list() returns the list or an empty set."""
        self.status = self.filesets_list() and 'Valid' or 'Invalid'
        self.save()
    
    def filesets_list(self):
        """Get list of associated file sets."""
        return FileSet.objects.filter(procedure=self.id)

    def schedules_list(self):
        """Get list of associated schedules."""
        return Schedule.objects.filter(procedure=self.id)

    def pools_list(self):
        """Get list of associated pools."""
        return Pool.objects.filter(procedure=self.id)
    
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

    def __unicode__(self):
        return self.procedure_name


### Schedule ###
class Schedule(models.Model):
    procedure = models.ForeignKey(Procedure)
    type = models.CharField("Nível",max_length=20,choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, default="Invalid")

    def update_status(self):
        """Changes status to valid or invalid depending if get_trigger() returns the trigger of False."""
        self.status = (self.get_trigger()) and 'Valid' or 'Invalid'
        self.save()

    def get_trigger(self):
        """Returns the associated trigger or False in case of it doesnt exist."""
        cmd = "trigger = %sTrigger.objects.get(schedule=self)" % (self.type)
        try:
            exec(cmd)
        except Exception, e: # DoesNotExist Exception means there's no trigger
            trigger = False
        return trigger

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
        return "computer/%s/procedure/%s/schedule/%s" % (
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


### Pool ###
class Pool(models.Model):
    # pools are created when Procedure is created through signals
    procedure = models.ForeignKey(Procedure)
    
### External Device ###
class ExternalDevice(models.Model):
    device_name = models.CharField("Nome",max_length=50)
    uuid = models.CharField("Dispositivo", max_length=50, unique=True)
    mount_index = models.IntegerField(unique=True)

    def mount_cmd(self):
        """Returns unix mount command"""
        return '''mount UUID=%s /mnt/%s''' % (self.uuid, self.mount_index)

    def __unicode__(self):
        return self.device_name

    # ClassMethods
    def device_choices(cls):
        dev_choices = []
        dev_choices.append(['','---------'])
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

    def stub_device_choices(cls):
        """Stub definition for returning a test set of usb devices"""
        stub_choices = []
        stub_choices.append(['','---------'])
        stub_choices.append(['5Y3E6323','ROXO'])
        stub_choices.append(['1YAE635AB','luke'])
        stub_choices.append(['943255CB','preto'])
        
        return stub_choices
    stub_device_choices = classmethod(stub_device_choices)

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
    restriction_time = models.TimeField("Início Restrição")

    def __unicode__(self):
		return '%s' % self.restriction_time

### Bandwidth Restriction ###
class BandwidthRestriction(models.Model):
    dayoftheweek = models.ForeignKey(DayOfTheWeek)
    restrictiontime = models.ForeignKey(RestrictionTime)
    restriction_value = models.IntegerField("Limite de Upload")


    def __unicode__(self):
	day = DAYS_OF_THE_WEEK[self.dayoftheweek.day_name]
        #return '%shs %s %s kbps' % (self.restrictiontime,day,self.restriction_value)
        return '%shs %s %s kbps' % (self.restrictiontime,self.dayoftheweek,self.restriction_value)


###
###   Signals
###
import backup_corporativo.bkp.signals
