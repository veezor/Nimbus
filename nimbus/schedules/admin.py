#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf import settings
from django.contrib import admin

from nimbus.schedules.models import Schedule, Monthly, Daily, Hourly, Weekly

admin.site.register(Schedule)
admin.site.register(Monthly)
admin.site.register(Daily)
admin.site.register(Weekly)
admin.site.register(Hourly)
