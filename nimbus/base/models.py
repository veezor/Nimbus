#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from datetime import datetime

import uuid

from django.db import models
from django.conf import settings

from nimbus.base.exceptions import UUIDViolation


UUID_NONE="none"


def get_uuidhex_value():
    return uuid.uuid4().hex 

def new_uuid():
    uuid = UUID()
    uuid.save()
    return uuid


class SingletonBaseModel(models.Model):

    @classmethod
    def get_instance(cls):
        try:
            instance = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            if settings.LOG_DEBUG:
                logger = logging.getLogger(__name__)
                logger.info("get_instance called. Instance of %s not exist." % cls.__name__)
            instance = cls()
        return instance


    @classmethod
    def exists(cls):
        return cls.objects.all().count() > 0


    def save(self, *args, **kwargs):
        self.id = 1
        return super(SingletonBaseModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class UUID(models.Model):
    uuid_hex = models.CharField( editable=False,
                                 max_length=255,
                                 unique=True,
                                 default=get_uuidhex_value )
    created_on = models.DateTimeField(editable=False, default=datetime.now)


    def __unicode__(self):
        return u"%s %s" % (self.uuid_hex, self.created_on)




class UUIDBaseModel(models.Model):
    uuid = models.ForeignKey(UUID, default=new_uuid, blank=True, editable=False)

 
    @property
    def bacula_name(self):
        return "%s_%s" % ( self.uuid.uuid_hex, 
                           self.__class__.__name__.lower() )
   
 
    class Meta:
        abstract = True



class UUIDSingletonModel(UUIDBaseModel, SingletonBaseModel):

   class Meta:
        abstract = True

   def save(self, *args, **kwargs):
       UUIDBaseModel.save(self, *args, **kwargs)
       SingletonBaseModel.save(self, *args, **kwargs)






BaseModel = UUIDBaseModel

