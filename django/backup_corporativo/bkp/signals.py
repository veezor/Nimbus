#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import socket
import logging
from os import path
from xmlrpclib import ServerProxy

from django.db.models.signals import post_save, post_delete 
from django.conf import settings

from pybacula import BConsoleInitError

from backup_corporativo.bkp.bacula import Bacula
from backup_corporativo.bkp.models import *
from backup_corporativo.bkp.template import render_to_file









### Decorators ###

def connect_on(model, signal):

    def generic_connect(function):

        def function_wrapper(sender, instance, signal, *args, **kwargs):
            value = function(instance)
            try:
                bacula = Bacula()
                bacula.reload()
            except BConsoleInitError, e:
                logger = logging.getLogger(__name__)
                logger.error("Comunicação com o bacula falhou")
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



# Must be first
@connect_on(model=GlobalConfig, signal=post_save)
def update_console_file(gconf):
    """Update bconsole file"""

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "bconsole.conf")
    address = NetworkInterface.get_instance().inteface_address

    render_to_file( filename,
                    "bconsole",
                     director_name=gconf.director_bacula_name(),
                     director_address=address,
                     director_password=gconf.director_password,
                     director_port=gconf.director_port)   



@connect_on(model=GlobalConfig, signal=post_save)
def update_director_file(gconf):
    """Generate director file"""

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "bacula-dir.conf")


    sto = Storage.get_instance()

    render_to_file( filename,
                    "bacula-dir",
                    director_name=gconf.director_bacula_name(), 
                    director_port=gconf.director_port, 
                    director_password=gconf.director_password,
                    storage_name=sto.storage_bacula_name(), 
                    storage_ip=sto.storage_ip, 
                    storage_port=sto.storage_port, 
                    storage_password=sto.storage_password,
                    devices=Devices.objects.all(),
                    db_name=gconf.bacula_database_name(), 
                    db_user=gconf.bacula_database_user(), 
                    db_password=gconf.bacula_database_password())




@connect_on(model=GlobalConfig, signal=post_save)
def update_storage_file(gconf):
    """Update storage File"""

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "bacula-sd.conf")

    sto = Storage.get_instance()

    render_to_file( filename,
                    "bacula-sd",
                    name=sto.storage_bacula_name(),
                    port=def_sto.storage_port,
                    max_cur_jobs=100,
                    director_name=gconf.director_bacula_name(),
                    director_password=gconf.director_password)




#### Procedure #####

@connect_on(model=Procedure, signal=post_save)
def update_procedure_file(proc):
    """Procedure update file"""

    name = proc.procedure_bacula_name()

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "jobs", name)

    render_to_file( filename,
                    "job",
                    name=name,
                    schedule=proc.schedule_bacula_name(),
                    storage=proc.storage.storage_bacula_name(),
                    fileset=proc.fileset_bacula_name(),
                    priority="10",
                    offsite=proc.offsite_on,
                    offsite_param="-m %v",
                    level="Incremental", #CONSERTAR
                    client=proc.computer.computer_bacula_name(),
                    poll=proc.pool_bacula_name() )



@connect_on(model=Procedure, signal=post_delete)
def remove_procedure_file(proc):
    """remove procedure file"""
    base_dir,filepath = utils.mount_path(proc.procedure_bacula_name(),'jobs')
    utils.remove_or_leave(filepath)
   


#### Computer #####

@connect_on(model=Computer, signal=post_save)
def update_computer_file(comp):
    """Computer update file"""

    name = comp.computer_bacula_name()


    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "jobs", name)

    render_to_file( filename,
                    "computer",
                    name=name,
                    id=comp.computer_id,
                    password=comp.computer_password)



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

    proc = instance.procedure
    name = proc.fileset_bacula_name()
    fsets = proc.fileset_set.all()


    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "filesets", name)

    render_to_file( filename,
                    "fileset",
                    name=name,
                    files=[ f.path for f in fsets ])




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
    name = proc.pool_bacula_name()

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "pools", name)

    render_to_file( filename,
                    "pool",
                    name=name,
                    max_vol_bytes=1048576,
                    days=proc.retention_time)



@connect_on(model=Pool, signal=post_delete)
def remove_pool_file(instance):
    """pool remove file"""

    proc = instance.procedure
    base_dir,filepath = utils.mount_path( proc.pool_bacula_name(), 'pools')
    utils.remove_or_leave(filepath)




#Schedules

def update_schedule_file(proc):

    filename = proc.schedule_bacula_name()
    scheds = proc.schedule_set.all()
    runs =  [ "%s %s" % (r[1],[0])   for r in run_dict(scheds).items() ]

    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "config", "schedules", name)

    render_to_file( filename,
                    "schedule",
                    name=name,
                    runs=runs )



@connect_on(model=Procedure, signal=post_delete)
def remove_schedule_file(proc):
    base_dir,filepath = utils.mount_path(proc.schedule_bacula_name(),'schedules')
    utils.remove_or_leave(filepath)



### Timezone ###
@connect_on(model=TimezoneConfig, signal=post_save)
def update_system_timezone(instance):
    try:
        server = ServerProxy("http://localhost:8888")
        server.change_timezone(instance.tz_area)
    except socket.error:
        logger = logging.getLogger(__name__)
        logger.error("Conexao com nimbus-manager falhou")


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
        logger = logging.getLogger(__name__)
        logger.error("Conexao com nimbus-manager falhou")



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

    jobfilename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                            "config", "jobs", filename)

    sto = Storage.get_instance()

    render_to_file( jobfilename,
                    "job",
                    name="Upload offsite",
                    schedule="offsite_schedule",
                    level="Incremental",
                    storage=sto.storage_bacula_name(),
                    fileset="empty_fileset",
                    priority=10,
                    client="empty_client",
                    pool="empty_pool",
                    offsite=True,
                    offsite_param="-u")


    schfilename = path.join( settings.NIMBUS_CUSTOM_PATH,
                             "config", "schedules", "offsite_sched")

    render_to_file( schfilename,
                    "schedule",
                    name="offsite_schedule",
                    runs=["Run = daily at %s" % offsite_hour])
    




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
            else: #'Monthly'
                days = trigg.target_days.split(';')
                for day in days:
                    key = "monthly %s at %s" % (day,str(trigg.hour.strftime("%H:%M")))
                    dict[key] = trigg.level
    return dict





@connect_on(model=Schedule, signal=post_save)
def update_schedule(instance):
    return update_schedule_file(instance.procedure)


@connect_on(model=WeeklyTrigger, signal=post_save)
def update_weekly_trigger(instance):
    return update_schedule_file(instance.schedule.procedure)

@connect_on(model=MonthlyTrigger, signal=post_save)
def update_monthly_trigger(instance):
    return update_schedule_file(instance.schedule.procedure)


    



