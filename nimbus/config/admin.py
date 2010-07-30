#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.conf import settings
from django.contrib import admin

from nimbus.config.models import Config
admin.site.register(Config)
