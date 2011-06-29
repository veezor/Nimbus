#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf import settings
from django.contrib import admin

from nimbus.schedules.models import Schedule, Month, Day, Hour, Week, BackupLevel, BackupKind, Run

admin.site.register(Schedule)
admin.site.register(Run)
admin.site.register(BackupLevel)
admin.site.register(BackupKind)
admin.site.register(Month)
admin.site.register(Day)
admin.site.register(Week)
admin.site.register(Hour)
