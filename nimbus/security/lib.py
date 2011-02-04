#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.contrib.contenttypes.models import ContentType

from nimbus.security.models import AdministrativeModel
from nimbus.security.exceptions import AdministrativeModelError



def check_permission(model):

    contenttype = ContentType.objects.get_for_model(model.__class__)
    if AdministrativeModel.objects\
            .filter(content_type=contenttype,
                    object_id=model.id,).count():
        raise AdministrativeModelError("Model is read-only")
