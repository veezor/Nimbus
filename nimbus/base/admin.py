#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.base import models

admin.site.register(models.UUID)
