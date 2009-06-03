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
# debug     import pdb; pdb.set_trace()


#
#   Main Definitions
#

# create associated pools to the procedure 
def create_pools(sender, instance, signal, *args, **kwargs):
    if 'created' in kwargs:
        if kwargs['created']:   # instance was just created
            ipool = Pool(procedure=instance,level='Incremental')
            ipool.save()
            fpool = Pool(procedure=instance,level='Full')
            fpool.save()

# updates statuses for procedure and schedule objects
def update_rel_statuses(sender, instance, signal, *args, **kwargs):
    if sender == FileSet:
        instance.procedure.update_status()
    elif ((sender == WeeklyTrigger) or (sender == MonthlyTrigger) or (sender == UniqueTrigger)):
        instance.schedule.update_status()

# entry point for update files
def update_files(sender, instance, signal, *args, **kwargs):
    if sender == FileSet:
        update_fileset_file(instance.procedure)    
    elif sender == Computer:
        update_computer_file(instance)
    elif sender == Procedure:
        update_fileset_file(instance)
    else:
        # do nothing for now
        pass

# entry point for remove files
def remove_files(sender, instance, signal, *args, **kwargs):
    if sender == Computer:
        remove_computer_file(instance)
    elif sender == Procedure:
        remove_fileset_file(instance)
    else:
        # do nothing for now
        pass

#
#   Auxiliar Definitions
#

# Computer update file
def update_computer_file(instance):
    default_password = 'm4r14f4r1nh4'
    cdict = computer_dict(instance.name,instance.ip,default_password)
    generate_computer_file(instance.name,cdict)

# generate attributes dict
def computer_dict(name,ip,senha):
    return {'Name':name, 'Address':ip, 'FDPort':'9102', 'Catalog':'MyCatalog',
    'password':senha, 'File Retention':'30 days', 'Job Retention':'6 months', 'AutoPrune':'yes'}

# Computer generate file    
def generate_computer_file(name,attr_dict):        
    f = prepare_to_write(name,'custom/computers')

    f.write("Client {\n")
    for k in attr_dict.keys():
        f.write('''\t%(key)s = "%(value)s"\n''' % {'key':k,'value':attr_dict[k]})
    f.write("}\n")
    f.close()

# Computer remove file
def remove_computer_file(instance):
    base_dir,filepath = mount_path(instance.name,'custom/computers')
    remove_or_leave(filepath)
    

# FileSet update filesets to a procedure instance
def update_fileset_file(procedure):
    fsets = procedure.filesets_list()
    name = get_fileset_name(procedure.name)
    farray = generate_file_array(fsets)
    generate_fileset_file(name,farray)

# get fileset name
def get_fileset_name(procedure_name):
    return "%sSet" % (procedure_name)
    
# generate file_array
def generate_file_array(fsets):
    array = []
    for fset in fsets:
        array.append(fset.path)
    return array
    
# FileSet generate file    
def generate_fileset_file(name,file_array):
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

# remove FileSet file
def remove_fileset_file(procedure):
    name = get_fileset_name(procedure.name)
    base_dir,filepath = mount_path(name,'custom/filesets')
    remove_or_leave(filepath)    

#
#   File Handling Specific Definitions
#

# create dir if dont exists
def create_or_leave(dirpath):
    try:
        os.makedirs(dirpath)
    except OSError:
        if os.path.isdir(dirpath):
            # Leave
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

# remove file if exists            
def remove_or_leave(filepath):
    try:
        os.remove(filepath)
    except os.error:
        # Leave
        pass

# make sure base_dir exists and open filename        
def prepare_to_write(instance_name,rel_dir):
    base_dir,filepath = mount_path(instance_name,rel_dir)
    create_or_leave(base_dir)
    #remove_or_leave(filepath)
    return open(filepath, 'w')

def mount_path(instance_name,rel_dir):
    filename = str.lower(str(instance_name))
    root = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(root,rel_dir)
    filepath = os.path.join(base_dir,filename)
    return base_dir, filepath
    
    
#
#   Dispatcher Connection
#


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
# WeeklyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=WeeklyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=WeeklyTrigger)
# MonthlyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=MonthlyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=MonthlyTrigger)
# UniqueTrigger
models.signals.post_save.connect(update_rel_statuses, sender=UniqueTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=UniqueTrigger)