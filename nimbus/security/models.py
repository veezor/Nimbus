#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic



class AdministrativeModel(models.Model):
    content_type = models.ForeignKey(ContentType, null=False, blank=False)
    object_id = models.PositiveIntegerField(null=False, blank=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')




