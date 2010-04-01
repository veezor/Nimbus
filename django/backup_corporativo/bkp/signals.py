#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from xmlrpclib import ServerProxy
import socket

from django.db.models.signals import post_save, post_delete 


from backup_corporativo.bkp import utils
from backup_corporativo.bkp.bacula import Bacula
from backup_corporativo.bkp.models import *

from bconsole import BConsoleInitError


### Constants ###
DAYS_OF_THE_WEEK = (
    'sunday','monday','tuesday',
    'wednesday','thursday','friday',
    'saturday',
)


### Decorators ###

def connect_on(model, signal):

    def generic_connect(function):

        def function_wrapper(sender, instance, signal, *args, **kwargs):
            value = function(instance)
            try:
                bacula = Bacula()
                bacula.reload()
            except BConsoleInitError, e:
                pass
            return value


        function_wrapper.__name__ = function.__name__ + "_wrapper"


        if isinstance(signal, tuple):
            for sig in signal:
                sig.connect(function_wrapper, sender=model)
        else:
            signal.connect(function_wrapper, sender=model)

        return function_wrapper

    return generic_connect


###
###   Main Definitions
###

def create_pools(sender, instance, signal, *args, **kwargs):
    """create associated pools to the procedure."""

    if 'created' in kwargs and kwargs.get('created'):
        if kwargs['created']:   # instance was just created
            fpool = Pool(procedure=instance)
            fpool.save()



# Must be first
@connect_on(model=GlobalConfig, signal=post_save)
def update_console_file(gconf):
    """Update Console File"""

    dir_dict = console_dir_dict( gconf.director_bacula_name(), 
                                 gconf.director_port, 
                                 gconf.director_password)
    
    generate_console("bconsole.conf", dir_dict)



### Timezone ###
@connect_on(model=TimezoneConfig, signal=post_save)
def update_system_timezone(instance):
    try:
        server = ServerProxy("http://localhost:8888")
        server.change_timezone(instance.tz_area)
    except socket.error:
        pass


### NetworkInterface ###
@connect_on(model=NetworkInterface, signal=post_save)
def update_networks_file(instance):
    try:
        server = ServerProxy("http://localhost:8888")

        server.generate_interfaces( instance.interface_name, 
                instance.interface_address, 
                instance.interface_netmask, 
                "static",
                instance.interface_broadcast, 
                instance.interface_network, 
                instance.interface_gateway)
        server.generate_dns( instance.interface_dns1, instance.interface_dns2)
    except socket.error:
        pass




### Global Config ###

@connect_on(model=GlobalConfig, signal=post_save)
def update_config_file(gconf):
    """Config update file"""

    dir_dict = config_dir_dict(gconf.director_bacula_name(), 
                               gconf.director_port, gconf.director_password)

    sto = Storage.get_instance()
    sto_dict = config_sto_dict( sto.storage_bacula_name(), 
                                sto.storage_ip, 
                                sto.storage_port, 
                                sto.storage_password )

    cat_dict = config_cat_dict("MyCatalog", gconf.bacula_database_name(), 
                                gconf.bacula_database_user(), gconf.bacula_database_password())

    smsg_dict = config_msg_dict("Standard",gconf.admin_mail())
    dmsg_dict = config_msg_dict("Daemon",gconf.admin_mail())    
    
    generate_config("bacula-dir.conf", dir_dict, sto_dict, 
                    cat_dict, smsg_dict, dmsg_dict)



def config_dir_dict(dir_name, dir_port, dir_passwd):
    """generate config director attributes dict"""
    
    return {'Name':dir_name, 'DIRport':dir_port, 
            'QueryFile':'"/opt/bacula/etc/bacula/query.sql"', 
            'WorkingDirectory':'"/opt/bacula/var/bacula/working"', 
            'PidDirectory':'"/opt/bacula/var/run"', 
            'Maximum Concurrent Jobs':'100',
            'Password':'"%s"' % dir_passwd, 
            'Messages':'Daemon' }




def config_sto_dict(name, ip, port, password):
    """generate config storage attributes dict"""
    
    return {'Name':name, 'Address':ip,'SDPort':port, 
            'Password':'"%s"' % password,
            'Device':'FileStorage','Media Type':'File'}




def config_cat_dict(cat_name, db_name, db_user, db_passwd):
    """generate config storage attributes dict"""
    
    return {'Name':cat_name, 'dbname':'"%s"' % db_name, 
            'dbuser':'"%s"' % db_user, 'dbpassword':'"%s"' % db_passwd}



def config_msg_dict(msg_name, admin_mail="backup@linconet.com.br"):
    """generate config message attributes dict"""

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
        'append':'"/opt/bacula/var/bacula/working/log" = all, !skipped'}



def _write_section(name, fileobj, dictobj):

    fileobj.write("%s {\n" % name)
    for key,value in dictobj.items():
        fileobj.write('''\t%s = %s\n''' % (key, value))
    fileobj.write("}\n\n")



def generate_config(filename,dir_dict, sto_dict, cat_dict, smsg_dict, dmsg_dict):
    """generate config file"""
    fileobj = utils.prepare_to_write(filename,'config/')
    
    _write_section("Director", fileobj, dir_dict)

    # sto_dict is now sto_dict.
    _write_section("Storage", fileobj, sto_dict)
    
    _write_section("Catalog", fileobj, cat_dict)
    _write_section("Messages", fileobj, smsg_dict)
    _write_section("Messages", fileobj, dmsg_dict)
    
    
    folders = ['computers','filesets','jobs','pools','schedules']
    for folder in folders:
        import_dir = utils.absolute_dir_path("%s/" % folder)
        fileobj.write("@|\"sh -c 'for f in %s* ; do echo @${f} ; done'\"\n" % import_dir)

    fileobj.close()



@connect_on(model=GlobalConfig, signal=post_save)
def update_offsite_file(gconf):

    if gconf.offsite_on:
        generate_offsite_file("offsite_job",gconf.offsite_hour)
    else:
        filepath = utils.absolute_file_path("offsite_job",'jobs')
        utils.remove_or_leave(filepath)
        filepath = utils.absolute_file_path('offsite_sched', 'schedules')
        utils.remove_or_leave(filepath)



def generate_offsite_file(filename, offsite_hour):

    f = utils.prepare_to_write(filename, 'jobs')
    sto = Storage.get_instance()
    sto.storage_name
    
    proc_dict = procedure_dict("Upload Offsite", False, "empty_client", 
                               "empty_fileset", "offsite_schedule", 
                               'empty_pool', sto.storage_bacula_name(), 'Admin', None)
    

    del(proc_dict['Run After Job'])
    
    f.write("Job {\n")
    for k in proc_dict.keys():
        f.write('''\t%(key)s = %(value)s\n''' % {'key':k,'value':proc_dict[k]})
    f.write('''\tRun After Job = "/var/django/NimbusClient/NimbusClient.py -u"\n''')
    f.write("}\n\n")
    f.close()
    
    f = utils.prepare_to_write('offsite_sched', 'schedules')
    
    f.write("Schedule {\n")
    f.write('''\tName = "%s"\n''' % 'offsite_sched')
    f.write('''\tRun = daily at %s\n''' %  offsite_hour)
    f.write("}\n")
    f.close()
    


### Device ###

def device_sto_dict(sto_name, sto_port):
    """generate device storage attributes dict"""
    
    return { 'Name':sto_name, 'SDPort':sto_port, 
             'WorkingDirectory':'"/opt/bacula/var/bacula/working"',
             'Pid Directory':'"/opt/bacula/var/run"','Maximum Concurrent Jobs':'20'}



def device_dir_dict(dir_name, dir_passwd):
    """generate device director attributes dict"""
    
    return {'Name':dir_name, 'Password':'"%s"' % dir_passwd}



def device_dev_dict(dev_name):
    """generate device device attributes dict"""
    
    return { 'Name':dev_name, 'Media Type':'File', 
            'Archive Device':'/opt/bacula/var/backup', 'LabelMedia':'yes', 
            'Random Access':'yes', 'AutomaticMount':'yes', 
            'RemovableMedia':'no', 'AlwaysOpen':'no'}



def device_msg_dict(msg_name, dir_name):
    """generate device message attributes dict"""
    
    return {'Name':msg_name, 'Director':'%s = all' % dir_name}

   

@connect_on(model=GlobalConfig, signal=post_save)
def update_device_file(gconf):
    """Update Device File"""
    def_sto = Storage.get_instance()
    sto_dict = device_sto_dict(def_sto.storage_bacula_name(), def_sto.storage_port)
    dir_dict = device_dir_dict(gconf.director_bacula_name(),def_sto.storage_password)
    dev_dict = device_dev_dict("FileStorage")
    msg_dict = device_msg_dict("Standard","%s" % gconf.director_bacula_name())
    generate_device("bacula-sd.conf", sto_dict, dir_dict, dev_dict, msg_dict)



def generate_device(filename,sto_dict, dir_dict, dev_dict, msg_dict):
    """generate config file"""
    f = utils.prepare_to_write(filename,'config/')

    _write_section("Storage", f, sto_dict)
    _write_section("Director", f, dir_dict)
    _write_section("Device", f, dev_dict)
    _write_section("Messages", f, msg_dict)
    
    f.close()


### Console ###

def console_dir_dict(dir_name, dir_port, dir_passwd):
    """generate device message attributes dict"""
    
    iface = NetworkInterface.get_instance()
    return { 'Name':dir_name, 'DIRPort':dir_port, 
             'Address':iface.interface_address, 'Password':'"%s"' % dir_passwd }



    


def generate_console(filename, dir_dict):
    """generate console file"""

    f = utils.prepare_to_write(filename,'config/')
    _write_section("Director", f, dir_dict)
    f.close()



#### Procedure #####

@connect_on(model=Procedure, signal=post_save)
def update_procedure_file(proc):
    """Procedure update file"""

    proc_name = proc.procedure_bacula_name()
    proc_offsite = proc.offsite_on
    restore_name = proc.restore_bacula_name()
    fset_name = proc.fileset_bacula_name()
    sched_name = proc.schedule_bacula_name()
    pool_name = proc.pool_bacula_name()
    comp_name = proc.computer.computer_bacula_name()
    sto_name = proc.storage.storage_bacula_name()

    jdict = procedure_dict(proc_name, proc_offsite, comp_name, 
                           fset_name, sched_name, pool_name, 
                           sto_name, type='Backup')

    generate_procedure(proc_name,jdict)

    

def procedure_dict(proc_name, proc_offsite, comp_name, fset_name, sched_name,
                   pool_name, sto_name, type='Backup', where=None):
    """generate procedure attributes dict"""
    
    bootstrap = '/opt/bacula/var/lib/bacula/%s.bsr' % (proc_name)
    run_after_job = proc_offsite and "/var/django/NimbusClient/NimbusClient.py -m %v" or None

    return  {'Name':proc_name, 'Client':comp_name, 'Level':'Incremental','FileSet':fset_name,
            'Schedule':sched_name, 'Storage':sto_name, 'Pool':pool_name,'Write Bootstrap':bootstrap,
            'Priority':'10', 'Messages':'Standard','Type':type,'Where':where, 'Run After Job':run_after_job,
    }



def generate_procedure(proc_name,attr_dict):
    """generate procedure file"""

    f = utils.prepare_to_write(proc_name,'jobs')

    f.write("Job {\n")

    if attr_dict['Run After Job'] is None:
        del(attr_dict['Run After Job'])

    if attr_dict['Type'] == 'Backup':
        f.write('''\tWrite Bootstrap = "%s"\n''' % (attr_dict['Write Bootstrap']))
    elif attr_dict['Type'] == 'Restore':
        f.write('''\tWhere = "%s"\n''' % (attr_dict['Where']))
        del(attr_dict['Schedule'])
        del(attr_dict['Level'])    

    del(attr_dict['Where'])

    for key,value in attr_dict.items():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':key,'value': value})

    f.write("}\n")
    f.close()



@connect_on(model=Procedure, signal=post_delete)
def remove_procedure_file(proc):
    """remove procedure file"""

    base_dir,filepath = utils.mount_path(proc.procedure_bacula_name(),'jobs')
    utils.remove_or_leave(filepath)
   


#### Computer #####

@connect_on(model=Computer, signal=post_save)
def update_computer_file(comp):
    """Computer update file"""

    cdict = computer_dict( comp.computer_bacula_name(), 
                           comp.computer_ip, comp.computer_password)

    generate_computer_file(comp.computer_bacula_name(),cdict)




def computer_dict(name,ip,password):
    """generate computer attributes dict"""

    return { 'Name':name, 'Address':ip, 'FDPort':'9102', 'Catalog':'MyCatalog',
    'password':password, 'AutoPrune':'yes'}



def generate_computer_file(name,attr_dict):
    """Computer generate file"""

    f = utils.prepare_to_write(name,'computers')
    _write_section("Client", f, attr_dict)
    f.close()



@connect_on(model=Computer, signal=post_delete)
def remove_computer_file(comp):
    """Computer remove file"""

    base_dir,filepath = utils.mount_path( comp.computer_bacula_name(), 
                                          'computers')
    utils.remove_or_leave(filepath)
   



#### FileSet #####

@connect_on(model=FileSet, signal=(post_save,post_delete))
def update_fileset_file(instance):
    """FileSet update filesets to a procedure instance"""

    if instance.__class__.__name__ == "FileSet":
        proc = instance.procedure
    else:
        proc = instance
    fsets = proc.fileset_set.all()
    fset_name = proc.fileset_bacula_name()
    farray = generate_file_array(fsets)
    generate_fileset_file(fset_name,farray)



def generate_file_array(fsets):
    """generate file_array"""

    array = []
    for fset in fsets:
        array.append(fset.path)
    return array
    


def generate_fileset_file(name,file_array):
    """FileSet generate file"""

    f = utils.prepare_to_write(name,'filesets')

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



@connect_on(model=Procedure, signal=post_delete)
def remove_fileset_file(proc):
    """remove FileSet file"""

    name = proc.fileset_bacula_name()
    base_dir,filepath = utils.mount_path(name,'filesets')
    utils.remove_or_leave(filepath)    



#### Pool #####

@connect_on(model=Pool, signal=post_save)
def update_pool_file(instance):
    """Pool update pool bacula file""" 

    proc = instance.procedure
    pool_name = proc.pool_bacula_name()
    pdict = pool_dict(pool_name)
    generate_pool(pool_name,pdict)



def pool_dict(pool_name):
    """Generate pool attributes dict"""

    format = '%s-vol-' % (pool_name)
    return {'Name':pool_name, 'Pool Type':'Backup', 
            'Recycle':'yes', 'AutoPrune':'yes', 
            'Volume Retention':'31 days','Purge Oldest Volume':'yes', 
            'Maximum Volume Bytes':'1048576',
            'Recycle Oldest Volume':'yes','Label Format':format}



def generate_pool(name,attr_dict):        
    """generate pool bacula file"""

    f = utils.prepare_to_write(name,'pools')
    
    f.write("Pool {\n")
    f.write("\tMaximum Volume Bytes = %s\n" % (attr_dict['Maximum Volume Bytes']))
    f.write("\tVolume Retention = %s\n" % (attr_dict['Volume Retention']))    

    del(attr_dict['Maximum Volume Bytes'])
    del(attr_dict['Volume Retention'])

    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})

    f.write("}\n")
    f.close()



@connect_on(model=Pool, signal=post_delete)
def remove_pool_file(instance):
    """pool remove file"""

    proc = instance.procedure
    base_dir,filepath = utils.mount_path( proc.pool_bacula_name(), 'pools')
    utils.remove_or_leave(filepath)



### Schedule ###
# TODO: Otimizar codigo, remover if do schedule type (programaçao dinamica)
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



@connect_on(model=Schedule, signal=post_save)
def update_schedule(instance):
    return update_schedule_file(instance.proc)



@connect_on(model=Schedule, signal=post_save)
def update_schedule(instance):
    return update_schedule_file(instance.procedure)



@connect_on(model=WeeklyTrigger, signal=post_save)
def update_weekly_trigger(instance):
    return update_schedule_file(instance.schedule.procedure)

@connect_on(model=MonthlyTrigger, signal=post_save)
def update_monthly_trigger(instance):
    return update_schedule_file(instance.schedule.procedure)


def update_schedule_file(proc):

    sched_name = proc.schedule_bacula_name()
    scheds = proc.schedule_set.all()
    rdict = run_dict(scheds)
    generate_schedule(sched_name,rdict)



def generate_schedule(schedule_name,run_dict):        

    f = utils.prepare_to_write(schedule_name,'schedules')

    f.write("Schedule {\n")
    f.write('''\tName = "%s"\n''' % (schedule_name))
    for k in run_dict.keys():
        f.write('''\tRun = %(level)s %(date)s\n''' % {'date':k,'level':run_dict[k]})    
    f.write("}\n")
    f.close()



@connect_on(model=Procedure, signal=post_delete)
def remove_schedule_file(proc):
    base_dir,filepath = utils.mount_path(proc.schedule_bacula_name(),'schedules')
    utils.remove_or_leave(filepath)
    


#### Storage #####
@connect_on(model=Storage, signal=post_save)
def update_storage_file(sto):
    """Storage update file."""

    sdict = storage_dict(sto.storage_bacula_name(),
                         sto.storage_ip,
                         sto.storage_port,
                         sto.storage_password)
    generate_storage_file(sto.storage_bacula_name(), sdict)



def storage_dict(name, ip, port, password):
    """Generate Storage attributes dict."""

    return {'Name': name, 'SDPort': port,
            'WorkingDirectory': '/opt/bacula/var/lib/bacula',
            'Pid Directory': '/opt/bacula/var/run',
            'Maximum Concurrent Jobs': 20}



def generate_storage_file(name, attr_dict):
    """Generate Storage file"""

    f = utils.prepare_to_write(name, 'storages')

    f.write("Storage {\n")
    for key,value in attr_dict.items():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':key, 'value': value})
    f.write("}\n")
    f.close()



@connect_on(model=Storage, signal=post_delete)
def remove_storage_file(sto):
    """Remove Storage file"""

    base_dir,filepath = utils.mount_path(sto.storage_bacula_name(), 'storages')
    utils.remove_or_leave(filepath)
