from django.db import models

# Some constants
TYPE_CHOICES = (
    ('Weekly', 'Weekly'),
    ('Monthly', 'Monthly'),
    ('Unique','Unique'),
)

LEVEL_CHOICES = (
    ('Full', 'Full'),
    ('Incremental', 'Incremental'),
)

DAYS_OF_THE_WEEK = (
    'sunday','monday','tuesday',
    'wednesday','thursday','friday',
    'saturday',
)


#
#   Models
#


# Computer
class Computer(models.Model):
    name = models.CharField(max_length=50)
    ip = models.IPAddressField()
    description = models.CharField(max_length=100)
    
    # get list of associated procedures
    def procedures_list(self):
        return Procedure.objects.filter(computer=self.id)

    def __unicode__(self):
        return self.name
        
# Procedure
class Procedure(models.Model):
    computer = models.ForeignKey(Computer)
    name = models.CharField(max_length=50)
    restore_path = models.CharField(max_length="255")
    status = models.CharField(max_length=10, default="Invalid")

    # change status to valid or invalid depending if filesets_list() returns the list or an empty set
    def update_status(self):
        self.status = self.filesets_list() and 'Valid' or 'Invalid'
        self.save()
    
    # get list of associated file sets    
    def filesets_list(self):
        return FileSet.objects.filter(procedure=self.id)

    # get list of associated schedules
    def schedules_list(self):
        return Schedule.objects.filter(procedure=self.id)

    # get list of associated pools        
    def pools_list(self):
        return Pool.objects.filter(procedure=self.id)

    def __unicode__(self):
        return self.name


# Schedule
class Schedule(models.Model):
    procedure = models.ForeignKey(Procedure)
    type = models.CharField(max_length=20,choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, default="Invalid")

    # change status to valid or invalid depending if get_trigger() returns the trigger of False
    def update_status(self):
        self.status = (self.get_trigger()) and 'Valid' or 'Invalid'
        self.save()

    # return the associated trigger or False in case of it doesnt exist
    def get_trigger(self):
        cmd = "trigger = %sTrigger.objects.get(schedule=self)" % (self.type)
        try:
            exec(cmd)
        except Exception, e: # DoesNotExist Exception means there's no trigger
            trigger = False
        return trigger
    
    def __unicode__(self):
        return self.procedure.name 


# WeeklyTrigger
class WeeklyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    for day in DAYS_OF_THE_WEEK:
        exec('%s = models.BooleanField()' % day)    
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)


# MonthlyTrigger
class MonthlyTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)
    target_days = models.CharField(max_length=100)


# UniqueTrigger
class UniqueTrigger(models.Model):
    schedule = models.ForeignKey(Schedule)
    target_date = models.DateField()
    hour = models.TimeField()
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)

# FileSet
class FileSet(models.Model):
    procedure = models.ForeignKey(Procedure)
    path = models.CharField(max_length="255")


# Pool
class Pool(models.Model):
    procedure = models.ForeignKey(Procedure)
    level = models.CharField(max_length=20,choices=LEVEL_CHOICES)
    
#
#   Signals
#

# create associated pools to the procedure 
def create_pools(sender, instance, signal,*args, **kwargs):
    if 'created' in kwargs:
        if kwargs['created']:   # instance was just created
            ipool = Pool(procedure=instance,level='Incremental')
            ipool.save()
            fpool = Pool(procedure=instance,level='Full')
            fpool.save()

# updates statuses for procedure and schedule objects
def update_rel_statuses(sender, instance, signal,*args, **kwargs):
    if sender == FileSet:   # need to update procedure
        instance.procedure.update_status()
    elif ((sender == WeeklyTrigger) or (sender == MonthlyTrigger) or (sender == UniqueTrigger)): # need to update schedule
        instance.schedule.update_status()
        
       
# Procedure    
models.signals.post_save.connect(create_pools, sender=Procedure)
# FileSet
models.signals.post_save.connect(update_rel_statuses, sender=FileSet)
models.signals.post_delete.connect(update_rel_statuses, sender=FileSet)
# WeeklyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=WeeklyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=WeeklyTrigger)
# MonthlyTrigger
models.signals.post_save.connect(update_rel_statuses, sender=MonthlyTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=MonthlyTrigger)
# UniqueTrigger
models.signals.post_save.connect(update_rel_statuses, sender=UniqueTrigger)
models.signals.post_delete.connect(update_rel_statuses, sender=UniqueTrigger)