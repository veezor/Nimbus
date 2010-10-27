#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.computers import models

admin.site.register(models.Computer)
admin.site.register(models.CryptoInfo)
admin.site.register(models.ComputerGroup)
