#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf import settings
from django.contrib import admin

from nimbus.backup.models import Schedule, Month, Day, Hour, Week, BackupLevel

admin.site.register(Schedule)
admin.site.register(Month)
admin.site.register(Day)
admin.site.register(Week)
admin.site.register(Hour)
admin.site.register(BackupLevel)