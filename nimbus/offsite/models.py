#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import logging
from time import time
from datetime import datetime
from urllib2 import URLError

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save

from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.shared import fields, signals
from nimbusgateway import Api


class Offsite(BaseModel):
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    gateway_url = models.CharField(max_length=255, editable=False,
                                   default="http://www.veezor.com:8080")
    upload_rate = models.IntegerField(default=-1)
    active = models.BooleanField()

    def clean(self):
        if self.active:
            try:
                api = Api(username=self.username,
                          password=self.password,
                          gateway_url=self.gateway_url)
                api.check_auth()
            except URLError, error:
                logger = logging.getLogger(__name__)
                logger.exception("Auth error")
                raise ValidationError("Impossível autenticar. Login ou senha não confere")


class Volume(models.Model):

    path = fields.ModelPathField(max_length=2048, null=False)
    size = models.IntegerField(null=False, editable=False, default=0)

    def __init__(self, *args, **kwargs):
        super(Volume, self).__init__( *args, **kwargs)
        if self.path and os.path.exists(self.path):
            self.size = os.path.getsize(self.path)

    @property
    def filename(self):
        return os.path.basename(self.path)


class OffSiteVolume(models.Model):
    volume = models.ForeignKey(Volume, null=False)
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        abstract = True


class UploadedVolume(OffSiteVolume):
    # WTF
    pass

class DownloadedVolume(OffSiteVolume):
    # WTF
    pass

class Request(models.Model):
    UPDATE_DIFF_SIZE_100_KB = 102400
    KB = 1024
    MB = KB * 1024
    MINUTES = 60
    HOURS = MINUTES * 60
    volume = models.ForeignKey(Volume, unique=True, null=False)
    created_at = models.DateTimeField(default=datetime.now, editable=False)
    attempts = models.PositiveSmallIntegerField(default=0, editable=False)
    last_attempt = models.DateTimeField(null=True, editable=False)
    last_update = models.IntegerField(default=0, editable=False) #unix time seconds
    transferred_bytes = models.IntegerField(default=0, editable=False)
    rate = models.IntegerField(default=0, editable=False)

    def update(self, new_bytes_size, total_bytes):
        bytesdiff = new_bytes_size - self.transferred_bytes
        if bytesdiff >= self.UPDATE_DIFF_SIZE_100_KB:
            if self.last_update:
                timediff = int(time() - self.last_update) or 1
                self.rate = bytesdiff / timediff
            self.last_update = time()
            self.transferred_bytes = new_bytes_size
            self.save()

    @property
    def remaining_bytes(self):
        return self.volume.size - self.transferred_bytes

    @property
    def estimated_transfer_time(self):
        if self.rate == 0:
            return "stalled"
        time = self.remaining_bytes / self.rate
        hours,seconds = divmod(time, self.HOURS)
        minutes,seconds = divmod(seconds, self.MINUTES)
        return "%dh%dm%ds" % (hours, minutes, seconds)

    @property
    def finished_percent(self):
        if self.volume.size == 0:
            return 100
        return "%.1f" % (float(self.transferred_bytes * 100) / self.volume.size)

    @property
    def friendly_rate(self):
        if self.rate > self.MB:
            return  "%dMB/s" % (self.rate / self.MB)
        elif self.rate > self.KB:
            return  "%dKB/s" % (self.rate / self.KB)
        else:
            return "%dB/s" % self.rate

    class Meta:
        abstract = True


class UploadRequest(Request):

    def __unicode__(self):
        return u"UploadRequest(path=%s)" % self.volume.path

    def finish(self):
        volume = UploadedVolume(volume=self.volume)
        volume.save()
        UploadTransferredData.objects.create(bytes=self.transferred_bytes)
        self.delete()

    class Meta:
        abstract = True

class RemoteUploadRequest(UploadRequest):
    
    def __unicode__(self):
        return u"RemoteUploadRequest(path=%s)" % self.volume.path

class LocalUploadRequest(UploadRequest):

    def __unicode__(self):
        return u"LocalUploadRequest(path=%s)" % self.volume.path

    def update(self, new_bytes_size, total_bytes):
        # WTF
        pass


class DownloadRequest(Request):

    def __unicode__(self):
        return u"DownloadRequest(path=%s)" % self.volume.path

    def finish(self):
        volume = DownloadedVolume(volume=self.volume)
        volume.save()
        DownloadTransferredData.objects.create(bytes=self.transferred_bytes)
        self.delete()

    def update(self, new_bytes_size, total_bytes):
        if self.volume.size == 0:
            self.volume.size = total_bytes
        super(DownloadRequest, self).update(new_bytes_size, total_bytes)


class DeleteRequest(Request):
    # WTF
    pass


class TransferredData(models.Model):
    bytes = models.IntegerField(null=False)
    date = models.DateTimeField(null=False, default=datetime.now)

    class Meta:
        abstract = True


class UploadTransferredData( TransferredData ):
    # WTF
    pass


class DownloadTransferredData( TransferredData ):
    # WTF
    pass


def nimbus_self_backup_update_offsite_status(offsite):
    from nimbus.procedures.models import Procedure # loop
    try:
        procedure = Procedure.objects.get(id=1) # self backup
        procedure.offsite_on = offsite.active
        procedure.save(system_permission=True)
    except Procedure.DoesNotExist, error:
        pass


signals.connect_on( nimbus_self_backup_update_offsite_status, Offsite, post_save)