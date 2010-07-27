from django.db import models

from nimbus.base.models import BaseModel
from nimbus.shared import enums
# Create your models here.

LEVELS = tuple( (l,l) for l in enums.levels )  
WEEKDAYS = tuple( (d,d) for d in enums.weekdays )
MONTHDAYS = tuple( (d,d) for d in enums.days )


class Schedule(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False)

    def get_runs(self):
        return list(self.hourly_set.get_query_set()) +\
                list(self.daily_set.get_query_set()) +\
                list(self.monthly_set.get_query_set()) +\
                list(self.weekly_set.get_query_set())



class TriggerBase(models.Model):
    schedule = models.ForeignKey(Schedule, null=False, blank=False)
    level = models.CharField(max_length="25", null=False, 
                             blank=False, choices=LEVELS)
    hour = models.TimeField( null=False, blank = False) 

    @classmethod
    def type_name(cls):
        return cls.__name__.lower()

    def __unicode__(self):
        return self.run_str()

    class Meta:
        abstract = True


class Daily(TriggerBase):
    
    def run_str(self):
        return u"%s at %s" % ( self.type_name(),
                               self.hour.strftime("%H:%M") )



class Hourly(TriggerBase):
    
    def run_str(self):
        return u"%s at 00:%s" % ( self.type_name(),
                                  self.hour.strftime("%M") )


class Monthly(TriggerBase):
    day = models.IntegerField(null=False, blank=False, choices=MONTHDAYS)


    def run_str(self):
        return u"%s %d at %s" % ( self.type_name(), 
                                  int(self.day),
                                  self.hour.strftime("%H:%M") )



class Weekly(TriggerBase):
    day = models.CharField(null=False, blank=False,
                           max_length=4, choices=WEEKDAYS)


    def run_str(self):
        return u"%s %s at %s" % ( self.type_name(), 
                                  self.day,
                                  self.hour.strftime("%H:%M") )





