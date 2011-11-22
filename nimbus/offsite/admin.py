#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin

from nimbus.offsite import models

admin.site.register(models.Offsite)
admin.site.register(models.Volume)
admin.site.register(models.UploadedVolume)
admin.site.register(models.DownloadedVolume)
admin.site.register(models.DownloadRequest)
admin.site.register(models.OffsiteGraphicsData)