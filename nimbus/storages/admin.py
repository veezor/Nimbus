#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.storages import models

admin.site.register(models.Storage)
admin.site.register(models.Device)
admin.site.register(models.StorageGraphicsData)

