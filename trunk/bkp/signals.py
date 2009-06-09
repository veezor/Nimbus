#!/usr/bin/python
# -*- coding: utf-8 -*-


# Misc
from django.db import models
import os
import string
# Models
from backup_corporativo.bkp.models import Computer
from backup_corporativo.bkp.models import Procedure
from backup_corporativo.bkp.models import Schedule
from backup_corporativo.bkp.models import WeeklyTrigger
from backup_corporativo.bkp.models import MonthlyTrigger
from backup_corporativo.bkp.models import UniqueTrigger
from backup_corporativo.bkp.models import FileSet
from backup_corporativo.bkp.models import Pool


### Constants ###

DAYS_OF_THE_WEEK = (
    'sunday','monday','tuesday',
    'wednesday','thursday','friday',
    'saturday',
)


###
###   Main Definitions
###


def create_pools(sender, instance, signal, *args, **kwargs):
    "create associated pools to the procedure"
    if 'created' in kwargs:
        if kwargs['created']:   # instance was just created
            fpool = Pool(procedure=instance,level='remover atributo')
            fpool.save()

def update_rel_statuses(sender, instance, signal, *args, **kwargs):
    "updates statuses for procedure and schedule objects"
    if sender == FileSet:
        instance.procedure.update_status()
    elif ((sender == WeeklyTrigger) or (sender == MonthlyTrigger) or (sender == UniqueTrigger)):
        instance.schedule.update_status()

def update_files(sender, instance, signal, *args, **kwargs):
    "entry point for update files"
    if sender == FileSet:
        update_fileset_file(instance.procedure)
    elif sender == Computer:
        update_computer_file(instance)
    elif sender == Procedure:
        update_procedure_file(instance)
        update_fileset_file(instance)
        update_schedule_file(instance)        
    elif sender == Pool:
        update_pool_file(instance.procedure)
    elif sender == Schedule:
        update_schedule_file(instance.procedure)
    else:
        raise # Oops!

def remove_files(sender, instance, signal, *args, **kwargs):
    "entry point for remove files"
    if sender == Computer:
        remove_computer_file(instance)
    elif sender == Procedure:
        remove_procedure_file(instance)
        remove_fileset_file(instance)
        remove_schedule_file(instance)
    elif sender == Pool:
        remove_pool_file(instance.procedure)
    elif sender == Schedule:
        pass
    else:
        raise # Oops!

###
###   Auxiliar Definitions
###


#### Procedure #####

def update_procedure_file(instance):
    "Procedure update file"
    proc_name = instance.get_procedure_name()
    restore_name = instance.get_restore_name()
    fset_name = instance.get_fileset_name()
    sched_name = instance.get_schedule_name()
    pool_name = instance.get_pool_name()
    comp_name = instance.computer.get_computer_name()
    jdict = procedure_dict(proc_name,'Backup',comp_name,fset_name,sched_name,pool_name)
    generate_procedure(proc_name,jdict)
    rdict = procedure_dict(restore_name,'Restore',comp_name,fset_name,sched_name,pool_name,instance.restore_path)
    generate_procedure(restore_name,rdict)
    
def procedure_dict(proc_name, type, computer_name, fset_name, sched_name, pool_name, where=None):
    "generate procedure attributes dict"
    bootstrap = '/var/lib/bacula/%s.bsr' % (proc_name)
    
    return {'Name':proc_name, 'Client':computer_name, 'Level':'Incremental', 
    'FileSet':fset_name, 'Schedule':sched_name, 'Storage':'LinconetStorage', 'Pool':pool_name, 
    'Write Bootstrap':bootstrap, 'Priority':'10', 'Messages':'Standard','Type':type,'Where':where}

def generate_procedure(proc_name,attr_dict):
    "generate procedure file"
    f = prepare_to_write(proc_name,'custom/jobs')

    f.write("Job {\n")
    if attr_dict['Type'] == 'Backup':
        f.write('''\tWrite Bootstrap = "%s"\n''' % (attr_dict['Write Bootstrap']))

    elif attr_dict['Type'] == 'Restore':
        f.write('''\tWhere = "%s"\n''' % (attr_dict['Where']))
        del(attr_dict['Schedule'])
        del(attr_dict['Level'])    
    del(attr_dict['Where'])
    del(attr_dict['Write Bootstrap'])
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_procedure_file(instance):
    "remove procedure file"
    base_dir,filepath = mount_path(instance.get_procedure_name(),'custom/jobs')
    remove_or_leave(filepath)
    base_dir,filepath = mount_path(instance.get_restore_name(),'custom/jobs')
    remove_or_leave(filepath)
    
#### Computer #####

def update_computer_file(instance):
    "Computer update file"
    default_password = 'm4r14f4r1nh4'
    cdict = computer_dict(instance.get_computer_name(),instance.ip,default_password)
    generate_computer_file(instance.get_computer_name(),cdict)

def computer_dict(name,ip,senha):
    "generate computer attributes dict"
    return {'Name':name, 'Address':ip, 'FDPort':'9102', 'Catalog':'MyCatalog',
    'password':senha, 'AutoPrune':'yes'}

def generate_computer_file(name,attr_dict):        
    "Computer generate file    "
    f = prepare_to_write(name,'custom/computers')

    f.write("Client {\n")
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_computer_file(instance):
    "Computer remove file"
    base_dir,filepath = mount_path(instance.get_computer_name(),'custom/computers')
    remove_or_leave(filepath)
    
#### FileSet #####


def update_fileset_file(procedure):
    "FileSet update filesets to a procedure instance"
    fsets = procedure.filesets_list()
    name = procedure.get_fileset_name()
    farray = generate_file_array(fsets)
    generate_fileset_file(name,farray)

def generate_file_array(fsets):
    "generate file_array"
    array = []
    for fset in fsets:
        array.append(fset.path)
    return array
    
def generate_fileset_file(name,file_array):
    "FileSet generate file    "
    f = prepare_to_write(name,'custom/filesets')

    f.write("FileSet {\n")
    f.write('''\tName = "%s"\n''' % (name))
    f.write("\tInclude {\n")
    f.write("\t\tOptions{\n")
    f.write('''\t\t\tsignature = "MD5"\n''')
    f.write('''\t\t\tcompression = "GZIP"\n''')
    f.write("\t\t}\n")
    for k in file_array:
        f.write('''\t\tFile = "%s"\n''' % (k))
    f.write("\t}\n")
    f.write("}\n")
    f.close()

def remove_fileset_file(procedure):
    "remove FileSet file"
    name = procedure.get_fileset_name()
    base_dir,filepath = mount_path(name,'custom/filesets')
    remove_or_leave(filepath)    

#### Pool #####

def update_pool_file(procedure):
    "Pool update pool bacula file"
    pool_name = procedure.get_pool_name()
    pdict = pool_dict(pool_name)
    generate_pool(pool_name,pdict)


def pool_dict(pool_name):
    "Generate pool attributes dict"
    format = '%s-vol-' % (pool_name)
    return {'Name':pool_name, 'Pool Type':'Backup', 'Recycle':'yes', 'AutoPrune':'yes', 
    'Volume Retention':'31 days','Purge Oldest Volume':'yes','Maximum Volume Bytes':'1048576',
    'Recycle Oldest Volume':'yes','Label Format':format}

def generate_pool(name,attr_dict):        
    "generate pool bacula file"
    f = prepare_to_write(name,'custom/pools')
    
    f.write("Pool {\n")
    f.write("\tMaximum Volume Bytes = %s\n" % (attr_dict['Maximum Volume Bytes']))
    f.write("\tVolume Retention = %s\n" % (attr_dict['Volume Retention']))    
    del(attr_dict['Maximum Volume Bytes'])
    del(attr_dict['Volume Retention'])
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_pool_file(instance):
    "pool remove file"
    base_dir,filepath = mount_path(instance.get_pool_name(),'custom/pools')
    remove_or_leave(filepath)

### Schedule ###

def run_dict(schedules_list):
    "build a dict with bacula run specification"
    dict = {}
    for sched in schedules_list:
        trigg = sched.get_trigger()
        if trigg:
            if sched.type == 'Weekly':
                days = []
                for day in DAYS_OF_THE_WEEK:
                    if getattr(trigg, day, None):
                        key = "%s at %s" % (day,str(trigg.hour.strftime("%H:%M")))
                        dict[key] = trigg.level
            elif sched.type == 'Monthly':
                days = trigg.target_days.split(';')
                for day in days:
                    key = "monthly %s at %s" % (day,str(trigg.hour.strftime("%H:%M")))
                    dict[key] = trigg.level
            else:
                # unique type still needs to be implemented
                raise
        else:
            # there's no trigger configured
            pass
    return dict


def update_schedule_file(procedure):
    sched_name = procedure.get_schedule_name()
    scheds = procedure.schedules_list()
    rdict = run_dict(scheds)
    generate_schedule(sched_name,rdict)

def generate_schedule(schedule_name,run_dict):        
    f = prepare_to_write(schedule_name,'custom/schedules')

    f.write("Schedule {\n")
    f.write('''\tName = "%s"\n''' % (schedule_name))
    for k in run_dict.keys():
        f.write('''\tRun = %(level)s %(date)s\n''' % {'date':k,'level':run_dict[k]})    
    f.write("}\n")
    f.close()

def remove_schedule_file(procedure):
    base_dir,filepath = mount_path(procedure.get_schedule_name(),'custom/schedules')
    remove_or_leave(filepath)
    


###
###   File Handling Specific Definitions
###

def create_or_leave(dirpath):
    "create dir if dont exists"
    try:
        os.makedirs(dirpath)
    except OSError:
        if os.path.isdir(dirpath):
            # Leave
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def remove_or_leave(filepath):
    "remove file if exists"
    try:
        os.remove(filepath)
    except os.error:
        # Leave
        pass

def prepare_to_write(instance_name,rel_dir):
    "make sure base_dir exists and open filename"
    base_dir,filepath = mount_path(instance_name,rel_dir)
    create_or_leave(base_dir)
    return open(filepath, 'w')

def mount_path(instance_name,rel_dir):
    "mount absolute dir path and filepath"
    filename = str.lower(str(instance_name))
    root = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(root,rel_dir)
    filepath = os.path.join(base_dir,filename)
    return base_dir, filepath
    
    
###
###   Dispatcher Connection
###


# Computer
models.signals.post_save.connect(update_files, sender=Computer)
models.signals.post_delete.connect(remove_files, sender=Computer)
# Procedure    
models.signals.post_save.connect(create_pools, sender=Procedure)
models.signals.post_save.connect(update_files, sender=Procedure)
models.signals.post_delete.connect(remove_files, sender=Procedure)
# FileSet
models.signals.post_save.connect(update_rel_statuses, sender=FileSet)
models.signals.post_save.connect(update_files, sender=FileSet)
models.signals.post_delete.connect(update_rel_statuses, sender=FileSet)
models.signals.post_delete.connect(update_files, sender=FileSet)
# Schedule
models.signals.post_save.connect(update_files, sender=Schedule)
models.signals.post_delete.connect(remove_files, sender=Schedule)
# WeeklyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=WeeklyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=WeeklyTrigger)
# MonthlyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=MonthlyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=MonthlyTrigger)
# UniqueTrigger
models.signals.post_save.connect(update_rel_statuses, sender=UniqueTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=UniqueTrigger)
# Pool
models.signals.post_save.connect(update_files, sender=Pool)
models.signals.post_delete.connect(remove_files, sender=Pool)