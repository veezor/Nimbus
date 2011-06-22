#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic



class AdministrativeModel(models.Model):
    content_type = models.ForeignKey(ContentType, null=False, blank=False)
    object_id = models.PositiveIntegerField(null=False, blank=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')



def register_object(model):
    adm_model = AdministrativeModel.objects.create(content_object=model)


def register_object_from_id(content_type, object_id):
    model_object = content_type.get_object_for_this_type(id=object_id)
    return register_object(model_object)


def register_object_from_model_name(app_label, model_name, object_id):
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    return register_object_from_id( content_type, object_id)


def register_objects_from_tuple(*args):
    for app_label, model_name, object_id in args:
        register_object_from_model_name(app_label, model_name, object_id)


def register_administrative_nimbus_models():
    register_objects_from_tuple(
            ("computers", "computer", 1),
            ("computers", "cryptoinfo", 1),
            ("filesets", "fileset", 1),
            ("filesets", "filepath", 1),
            ("filesets", "filepath", 2),
            ("filesets", "filepath", 3),
            ("schedules", "schedule", 1),
            ("schedules", "day", 1),
            ("schedules", "hour", 1),
            ("schedules", "backuplevel", 1),
            ("schedules", "backuplevel", 2),
            ("procedures", "procedure", 1),
            ("storages", "storage", 1),
            ("storages", "device", 1),
    )


