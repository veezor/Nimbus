#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from datetime import datetime
import uuid
from django.db import models
from django.conf import settings
from nimbus.security.lib import check_permission
from nimbus.base.exceptions import UUIDViolation

UUID_NONE="none"
logger = logging.getLogger(__name__)


class Notification(models.Model):
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    ack = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s" % self.message

class SingletonBaseModel(models.Model):

    @classmethod
    def get_instance(cls):
        try:
            instance = cls.objects.get(pk=1)
        except cls.DoesNotExist:
            if settings.LOG_DEBUG:
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
    uuid_hex = models.CharField(editable=False,
                                max_length=255,
                                unique=True,
                                default=UUID_NONE)
    created_on = models.DateTimeField(editable=False, default=datetime.now)

    def __unicode__(self):
        return u"%s %s" % (self.uuid_hex, self.created_on)

    def save(self, *args, **kwargs):
        if self.uuid_hex == UUID_NONE:
            self.uuid_hex = uuid.uuid4().hex
            return super(UUID, self).save(*args, **kwargs)
        else:
            if settings.LOG_DEBUG:
                logger.error("UUIDViolation on %s" % self.__class__.__name__)
            raise UUIDViolation() 


class UUIDBaseModel(models.Model):
    uuid = models.ForeignKey(UUID, editable=False)

    def _generate_uuid(self):
        uuid = UUID()
        uuid.save()
        self.uuid = uuid

    def save(self, *args, **kwargs):
        try:
            self.uuid
        except UUID.DoesNotExist:
            self._generate_uuid()
        system_permission = kwargs.pop("system_permission", False)
        if not system_permission:
            check_permission(self)
        return super(UUIDBaseModel, self).save(*args, **kwargs)
 
    @property
    def bacula_name(self):
        return "%s_%s" % (self.uuid.uuid_hex, 
                          self.__class__.__name__.lower())
 
    class Meta:
        abstract = True


class UUIDSingletonModel(UUIDBaseModel, SingletonBaseModel):

   class Meta:
        abstract = True

   def save(self, *args, **kwargs):
       super(UUIDSingletonModel, self).save(*args, **kwargs)


BaseModel = UUIDBaseModel