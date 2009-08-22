#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.network_utils import NetworkInfo
from backup_corporativo.bkp.bacula import Bacula
from backup_corporativo.bkp.models import *


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
    """create associated pools to the procedure."""
    if 'created' in kwargs:
        if kwargs['created']:   # instance was just created
            fpool = Pool(procedure=instance)
            fpool.save()

def update_files(sender, instance, signal, *args, **kwargs):
    """entry point for update files"""
    from backup_corporativo.bkp.bacula import Bacula
    
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
    elif sender == WeeklyTrigger:
        update_schedule_file(instance.schedule.procedure)
    elif sender == MonthlyTrigger:
        update_schedule_file(instance.schedule.procedure)
    elif sender == Storage:
        update_storage_file(instance)
    elif sender == NetworkInterface:
    	update_iftab_file(instance)
    	update_interfaces_file(instance)
    	update_dns_file(instance)
    elif sender == GlobalConfig:
        update_default_storage(instance)
        update_config_file(instance)
        update_device_file(instance)     
        update_console_file(instance)
    elif sender == BandwidthRestriction:
        generate_cron()
    else:
        raise # Oops!
    Bacula.reload()

def remove_files(sender, instance, signal, *args, **kwargs):
    """entry point for remove files"""
    if sender == Computer:
        remove_computer_file(instance)
    elif sender == Procedure:
        remove_procedure_file(instance)
        remove_fileset_file(instance)
        remove_schedule_file(instance)
    elif sender == Pool:
        remove_pool_file(instance.procedure)
    elif sender == Storage:
        remove_storage_file(instance)
    elif sender == Schedule:
        pass
    else:
        raise # Oops!
    Bacula.reload()


### NetworkInterface ###
def update_iftab_file(instance):
	from SOAPpy import SOAPProxy
	server = SOAPProxy("http://127.0.0.1:8888")
	server.generate_iftab(instance.interface_name,instance.interface_mac)

def update_interfaces_file(instance):
	from SOAPpy import SOAPProxy
	server = SOAPProxy("http://127.0.0.1:8888")
	server.generate_interfaces(instance.interface_name, instance.interface_address, instance.interface_netmask, instance.interface_broadcast, instance.interface_network, instance.interface_gateway)

	
def update_dns_file(instance):
	from SOAPpy import SOAPProxy
	server = SOAPProxy("http://127.0.0.1:8888")
	server.generate_dns(instance.interface_dns1, instance.interface_dns2)
	
### Global Config ###

def update_config_file(instance):
    """Config update file"""
    i = instance
    dir_dict = config_dir_dict("%s" % i.bacula_name, i.director_port, i.director_password)
    sto_list = []
    for sto in Storage.objects.all():
        sto_list.append(config_sto_dict(sto.storage_name, sto.storage_ip, sto.storage_port, sto.storage_password))
    cat_dict = config_cat_dict("MyCatalog",i.database_name, i.database_user, i.database_password)
    smsg_dict = config_msg_dict("Standard",i.admin_mail)
    dmsg_dict = config_msg_dict("Daemon",i.admin_mail)    
    generate_config("bacula-dir.conf", dir_dict, sto_list, cat_dict, smsg_dict, dmsg_dict)

def config_dir_dict(dir_name, dir_port, dir_passwd):
    """generate config director attributes dict"""
    
    return {'Name':dir_name, 'DIRport':dir_port, 'QueryFile':'"/etc/bacula/query.sql"', 
    'WorkingDirectory':'"/var/bacula/working"','PidDirectory':'"/var/run"','Maximum Concurrent Jobs':'1',
    'Password':'"%s"' % dir_passwd, 'Messages':'Daemon' }

def config_sto_dict(name, ip, port, password):
    """generate config storage attributes dict"""
    
    return {'Name':name, 'Address':ip,'SDPort':port, 'Password':'"%s"' % password,
    'Device':'FileStorage','Media Type':'File'}

def config_cat_dict(cat_name, db_name, db_user, db_passwd):
    """generate config storage attributes dict"""
    
    return {'Name':cat_name, 'dbname':'"%s"' % db_name, 'dbuser':'"%s"' % db_user, 'dbpassword':'"%s"' % db_passwd}
    
def config_msg_dict(msg_name, admin_mail=None):
    """generate config message attributes dict"""
    admin_mail = admin_mail or "backup@linconet.com.br"
    if msg_name == 'Standard':
        return {'Name':msg_name, 
        'mailcommand':'"/sbin/bsmtp -h localhost -f \\"\(Bacula\) \<%r\>\\" -s \\"Bacula: %t %e of %c %l\\" %r"', 
        'operatorcommand':'"/sbin/bsmtp -h localhost -f \\"\(Bacula\) \<%r\>\\" -s \\"Bacula: Intervention needed for %j\\" %r"', 
        'mail':'%s = all, !skipped' % admin_mail, 'operator':'%s = mount' % admin_mail,
        'console':'all, !skipped, !saved', 'append':'"/var/bacula/working/log" = all, !skipped'}
    elif msg_name == 'Daemon':
        return {'Name':msg_name, 
        'mailcommand':'"/sbin/bsmtp -h localhost -f \\"\(Bacula\) \<%r\>\\" -s \\"Bacula daemon message\\" %r"',
        'mail':'%s = all, !skipped' % admin_mail, 'console':'all, !skipped, !saved', 
        'append':'"/var/bacula/working/log" = all, !skipped'}


    
def generate_config(filename,dir_dict, sto_list, cat_dict, smsg_dict, dmsg_dict):
    """generate config file"""
    f = utils.prepare_to_write(filename,'custom/config/')

    f.write("Director {\n")
    for k in dir_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
    f.write("}\n\n")

    # sto_dict is now sto_list.
    for sto in sto_list:
        f.write("Storage {\n")
        for k in sto.keys():
            f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':sto[k]})
        f.write("}\n\n")
    
    f.write("Catalog {\n")
    for k in cat_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':cat_dict[k]})
    f.write("}\n\n")
    
    f.write("Messages {\n")
    for k in smsg_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':smsg_dict[k]})
    f.write("}\n\n")

    f.write("Messages {\n")
    for k in dmsg_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dmsg_dict[k]})
    f.write("}\n\n")
    
    folders = ['computers','filesets','jobs','pools','schedules']
    for folder in folders:
        import_dir = utils.absolute_dir_path("custom/%s/" % folder)
        f.write("@|\"sh -c 'for f in %s* ; do echo @${f} ; done'\"\n" % import_dir)

    f.close()

### Device ###

def device_sto_dict(sto_name, sto_port):
    """generate device storage attributes dict"""
    
    return {'Name':sto_name, 'SDPort':sto_port, 'WorkingDirectory':'"/var/bacula/working"',
    'Pid Directory':'"/var/run"','Maximum Concurrent Jobs':'20'}

def device_dir_dict(dir_name, dir_passwd):
    """generate device director attributes dict"""
    
    return {'Name':dir_name, 'Password':'"%s"' % dir_passwd}

def device_dev_dict(dev_name):
    """generate device device attributes dict"""
    
    return {'Name':dev_name, 'Media Type':'File', 'Archive Device':'/var/backup', 'LabelMedia':'yes', 
    'Random Access':'yes', 'AutomaticMount':'yes', 'RemovableMedia':'no', 'AlwaysOpen':'no'}


def device_msg_dict(msg_name, dir_name):
    """generate device message attributes dict"""
    
    return {'Name':msg_name, 'Director':'%s = all' % dir_name}

    
def update_device_file(instance):
    """Update Device File"""
    i = instance
    def_sto = Storage.get_default_storage()
    sto_dict = device_sto_dict("StorageLocal", def_sto.storage_port)
    dir_dict = device_dir_dict("%s" % i.bacula_name,def_sto.storage_password)
    dev_dict = device_dev_dict("FileStorage")
    msg_dict = device_msg_dict("Standard","%s" % i.bacula_name)
    generate_device("bacula-sd.conf", sto_dict, dir_dict, dev_dict, msg_dict)

def generate_device(filename,sto_dict, dir_dict, dev_dict, msg_dict):
    """generate config file"""
    f = utils.prepare_to_write(filename,'custom/config/')

    f.write("Storage {\n")
    for k in sto_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':sto_dict[k]})
    f.write("}\n\n")

    f.write("Director {\n")
    for k in dir_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
    f.write("}\n\n")
    
    f.write("Device {\n")
    for k in dev_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dev_dict[k]})
    f.write("}\n\n")
    
    f.write("Messages {\n")
    for k in msg_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':msg_dict[k]})
    f.write("}\n\n")
    f.close()

### Console ###

def console_dir_dict(dir_name, dir_port, dir_passwd):
    """generate device message attributes dict"""
    
    return {'Name':dir_name, 'DIRPort':dir_port, 'Address':'127.0.0.1', 'Password':'"%s"' % dir_passwd}


def update_console_file(instance):
    """Update Console File"""
    i = instance
    dir_dict = console_dir_dict("%s" % i.bacula_name, i.director_port, i.director_password)
    generate_console("bconsole.conf", dir_dict)
    

def generate_console(filename,dir_dict):
    """generate console file"""
    f = utils.prepare_to_write(filename,'custom/config/')

    f.write("Director {\n")
    for k in dir_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':dir_dict[k]})
    f.write("}\n\n")


    
#### Procedure #####

def update_procedure_file(instance):
    """Procedure update file"""
    proc_name = instance.get_procedure_name()
    restore_name = instance.get_restore_name()
    fset_name = instance.get_fileset_name()
    sched_name = instance.get_schedule_name()
    pool_name = instance.get_pool_name()
    comp_name = instance.computer.get_computer_name()
    sto_name = instance.storage.storage_name
    jdict = procedure_dict(proc_name, comp_name, fset_name, sched_name, pool_name, sto_name, type='Backup')
    generate_procedure(proc_name,jdict)

    
def procedure_dict(proc_name, comp_name, fset_name, sched_name, pool_name, sto_name, type='Backup', where=None):
    """generate procedure attributes dict"""
    bootstrap = '/var/lib/bacula/%s.bsr' % (proc_name)
    
    return  {'Name':proc_name, 'Client':comp_name, 'Level':'Incremental','FileSet':fset_name,
            'Schedule':sched_name, 'Storage':sto_name, 'Pool':pool_name,'Write Bootstrap':bootstrap,
            'Priority':'10', 'Messages':'Standard','Type':type,'Where':where
            }

def generate_procedure(proc_name,attr_dict):
    """generate procedure file"""
    f = utils.prepare_to_write(proc_name,'custom/jobs')

    f.write("Job {\n")
    
    if attr_dict['Type'] == 'Backup':
        f.write('''\tWrite Bootstrap = "%s"\n''' % (attr_dict['Write Bootstrap']))
    elif attr_dict['Type'] == 'Restore':
        f.write('''\tWhere = "%s"\n''' % (attr_dict['Where']))
        del(attr_dict['Schedule'])
        del(attr_dict['Level'])    
    del(attr_dict['Where'])
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_procedure_file(instance):
    """remove procedure file"""
    base_dir,filepath = utils.mount_path(instance.get_procedure_name(),'custom/jobs')
    utils.remove_or_leave(filepath)
    
#### Computer #####

def update_computer_file(instance):
    """Computer update file"""
    cdict = computer_dict(instance.get_computer_name(),instance.computer_ip,instance.computer_password)
    generate_computer_file(instance.get_computer_name(),cdict)

def computer_dict(name,ip,password):
    """generate computer attributes dict"""
    return {'Name':name, 'Address':ip, 'FDPort':'9102', 'Catalog':'MyCatalog',
    'password':password, 'AutoPrune':'yes'}

def generate_computer_file(name,attr_dict):        
    """Computer generate file"""
    f = utils.prepare_to_write(name,'custom/computers')

    f.write("Client {\n")
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_computer_file(instance):
    """Computer remove file"""
    base_dir,filepath = utils.mount_path(instance.get_computer_name(),'custom/computers')
    utils.remove_or_leave(filepath)
    
#### FileSet #####


def update_fileset_file(procedure):
    """FileSet update filesets to a procedure instance"""
    fsets = procedure.fileset_set.all()
    name = procedure.get_fileset_name()
    farray = generate_file_array(fsets)
    generate_fileset_file(name,farray)

def generate_file_array(fsets):
    """generate file_array"""
    array = []
    for fset in fsets:
        array.append(fset.path)
    return array
    
def generate_fileset_file(name,file_array):
    """FileSet generate file"""
    f = utils.prepare_to_write(name,'custom/filesets')

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
    """remove FileSet file"""
    name = procedure.get_fileset_name()
    base_dir,filepath = utils.mount_path(name,'custom/filesets')
    utils.remove_or_leave(filepath)    

#### Pool #####

def update_pool_file(procedure):
    """Pool update pool bacula file""" 
    pool_name = procedure.get_pool_name()
    pdict = pool_dict(pool_name)
    generate_pool(pool_name,pdict)


def pool_dict(pool_name):
    """Generate pool attributes dict"""
    format = '%s-vol-' % (pool_name)
    return {'Name':pool_name, 'Pool Type':'Backup', 'Recycle':'yes', 'AutoPrune':'yes', 
    'Volume Retention':'31 days','Purge Oldest Volume':'yes','Maximum Volume Bytes':'1048576',
    'Recycle Oldest Volume':'yes','Label Format':format}

def generate_pool(name,attr_dict):        
    """generate pool bacula file"""
    f = utils.prepare_to_write(name,'custom/pools')
    
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
    """pool remove file"""
    base_dir,filepath = utils.mount_path(instance.get_pool_name(),'custom/pools')
    utils.remove_or_leave(filepath)

### Schedule ###
def run_dict(schedules_list):
    """build a dict with bacula run specification"""
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
            pass
    return dict


def update_schedule_file(procedure):
    sched_name = procedure.get_schedule_name()
    scheds = procedure.schedule_set.all()
    rdict = run_dict(scheds)
    generate_schedule(sched_name,rdict)

def generate_schedule(schedule_name,run_dict):        
    f = utils.prepare_to_write(schedule_name,'custom/schedules')

    f.write("Schedule {\n")
    f.write('''\tName = "%s"\n''' % (schedule_name))
    for k in run_dict.keys():
        f.write('''\tRun = %(level)s %(date)s\n''' % {'date':k,'level':run_dict[k]})    
    f.write("}\n")
    f.close()

def remove_schedule_file(procedure):
    base_dir,filepath = utils.mount_path(procedure.get_schedule_name(),'custom/schedules')
    utils.remove_or_leave(filepath)
    


#### Storage #####
def update_default_storage(globalconfig):
    """Updates default storage object or creates it if doesnt exists."""
    def_sto = Storage.get_default_storage()
    def_sto = def_sto and def_sto or Storage() # Assign new storage if it doesnt exist
    def_sto.storage_name = 'StorageLocal'
    def_sto.storage_ip = globalconfig.server_ip
    def_sto.storage_port = globalconfig.storage_port
    def_sto.save()


def update_storage_file(instance):
    """Storage update file."""
    sdict = storage_dict(instance.get_storage_name(),
                         instance.storage_ip,
                         instance.storage_port,
                         instance.storage_password)
    generate_storage_file(instance.get_storage_name(), sdict)

def storage_dict(name, ip, port, password):
    """Generate Storage attributes dict."""
    return {'Name': name, 'SDPort': port,
            'WorkingDirectory': '/var/lib/bacula',
            'Pid Directory': '/var/run',
            'Maximum Concurrent Jobs': 20}

def generate_storage_file(name, attr_dict):
    """Generate Storage file"""
    f = utils.prepare_to_write(name, 'custom/storages')

    f.write("Storage {\n")
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k, 'value':attr_dict[k]})
    f.write("}\n")
    f.close()

def remove_storage_file(instance):
    """Remove Storage file"""
    base_dir,filepath = utils.mount_path(instance.get_storage_name(), 'custom/storages')
    utils.remove_or_leave(filepath)



### Cron file
def generate_cron(filename="nimbus.cron"):
	"""Generates cron file"""
	import commands
	import time
	root_user = 'root'
	script_name = 'speedctl.py'
	f = utils.prepare_to_write(filename,'custom/')
	restrictions = BandwidthRestriction.objects.all()

	for rest in restrictions:
		hour = rest.restrictiontime.restriction_time.hour
		minute = rest.restrictiontime.restriction_time.minute
		week_day = rest.dayoftheweek.day_name[0:3]
		rest_value = rest.restriction_value
		f.write('%s %s * * %s %s %s %s\n' % (minute,hour,week_day,root_user,script_name,rest_value))
	f.close()

   
###
###   Dispatcher Connection
###

#NetworkConfig
models.signals.post_save.connect(update_files, sender=NetworkInterface)
# GlobalConfig
models.signals.post_save.connect(update_files, sender=GlobalConfig)
# Computer
models.signals.post_save.connect(update_files, sender=Computer)
models.signals.post_delete.connect(remove_files, sender=Computer)
# Procedure    
models.signals.post_save.connect(create_pools, sender=Procedure)
models.signals.post_save.connect(update_files, sender=Procedure)
models.signals.post_delete.connect(remove_files, sender=Procedure)
# FileSet
models.signals.post_save.connect(update_files, sender=FileSet)
models.signals.post_delete.connect(update_files, sender=FileSet)
# Schedule
models.signals.post_save.connect(update_files, sender=Schedule)
models.signals.post_delete.connect(remove_files, sender=Schedule)
# Pool
models.signals.post_save.connect(update_files, sender=Pool)
models.signals.post_delete.connect(remove_files, sender=Pool)
# Cron
models.signals.post_save.connect(update_files, sender=Storage)
models.signals.post_delete.connect(remove_files, sender=Storage)
# Cron
models.signals.post_save.connect(update_files, sender=BandwidthRestriction)
models.signals.post_delete.connect(update_files, sender=BandwidthRestriction)
# Trigger
models.signals.post_save.connect(update_files, sender=WeeklyTrigger)
models.signals.post_delete.connect(update_files, sender=WeeklyTrigger)
models.signals.post_save.connect(update_files, sender=MonthlyTrigger)
models.signals.post_delete.connect(update_files, sender=MonthlyTrigger)
