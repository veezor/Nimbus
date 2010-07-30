#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.timezone.models import Timezone
admin.site.register(Timezone)
