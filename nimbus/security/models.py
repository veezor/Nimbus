#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import pre_save, pre_delete

from nimbus.base.models import UUIDBaseModel 
from nimbus.procedures.models import Procedure
from nimbus.security.exceptions import AdministrativeModelError

class AdministrativeModel(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')



def is_administrative_model(sender, instance, **kwargs):

    if not isinstance(instance, UUIDBaseModel): # django.signals not support inheritance
        return

    contenttype = ContentType.objects.get_for_model(sender)
    if AdministrativeModel.objects\
            .filter(content_type=contenttype,object_id=instance.id).count():
        raise AdministrativeModelError("Model is read-only")


pre_save.connect( is_administrative_model)
pre_delete.connect( is_administrative_model)
