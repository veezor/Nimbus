#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.procedures import models

admin.site.register(models.Profile)
admin.site.register(models.Procedure)

