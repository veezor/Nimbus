#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import logging
from time import time
from datetime import datetime



from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete 


from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.storages.models import Storage
from nimbus.libs.template import render_to_file
from nimbus.shared import utils, signals


# Create your models here.

class Offsite(BaseModel):
    username = models.CharField(max_length=255, null=False, blank=False)
    password = models.CharField(max_length=255, null=False, blank=False)
    gateway_url = models.CharField( max_length=255,
                                    null=False,
                                    default="http://gatewaynimbus.veezor.com")
    upload_rate = models.IntegerField(default=-1,null=False)
    active = models.BooleanField(null=False)
    hour = models.TimeField()


class Volume(models.Model):

    path = models.FilePathField(null=False, unique=True)
    size = models.IntegerField(null=False)

    def __init__(self, *args, **kwargs):
        path = kwargs.get("path", None)
        if path:
            try:
                size = os.path.getsize(path)
            except OSError, e:
                size = 0
            super(Volume, self).__init__( size=size, *args, **kwargs)
        else:
            super(Volume, self).__init__(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.path)


    class Meta:
        app_label = 'bkp'




class OffSiteVolume(models.Model):
    volume = models.ForeignKey(Volume, null=False)
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        abstract = True
        app_label = 'bkp'



class UploadedVolume(OffSiteVolume):
    pass


class DownloadedVolume(OffSiteVolume):
    pass

class Request(models.Model):
    UPDATE_DIFF_SIZE_256_KB = 268435456
    KB = 1024
    MB = KB * 1024
    MINUTES = 60
    HOURS = MINUTES * 60

    volume = models.ForeignKey(Volume, unique=True, null=False)
    created_at = models.DateTimeField(default=datetime.now)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True)
    last_update = models.IntegerField(default=0) #unix time seconds
    transferred_bytes = models.IntegerField(default=0)
    rate = models.IntegerField(default=0)


    def update(self, new_bytes_size, total_bytes):
        bytesdiff = new_bytes_size - self.transferred_bytes
        if bytesdiff >= self.UPDATE_DIFF_SIZE_256_KB:
            timediff = int(time() - self.last_update)
            self.rate = bytesdiff / timediff
            self.transferred_bytes = bytes
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
        return "%dh%m%ds" % (hours, minutes, seconds)

    @property
    def finished_percent(self):
        if self.volume.size == 0:
            return 100
        return float(self.transferred_bytes) / self.volume.size

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
        app_label = 'bkp'




class UploadRequest(Request):


    def __str__(self):
        return "UploadRequest(path=%s)" % self.volume.path

    def finish(self):
        volume = UploadedVolume(volume=self.volume)
        volume.save()
        self.delete()



class DownloadRequest(Request):

    def __str__(self):
        return "DownloadRequest(path=%s)" % self.volume.path

    def finish(self):
        volume = DownloadedVolume(volume=self.volume)
        volume.save()
        self.delete()

    def update(self, new_bytes_size, total_bytes):
        if self.volume.size == 0:
            self.volume.size = total_bytes
        super(DownloadRequest, self).update(new_bytes_size, total_bytes)





def update_offsite_file(offsite):

    if offsite.active:
        generate_offsite_file(offsite.hour)
    else:
        job = os.path.join( settings.NIMBUS_JOBS_PATH, "offsite" )
        schedule = os.path.join( settings.NIMBUS_SCHEDULES_PATH, "offsite" )
        utils.remove_or_leave(job)
        utils.remove_or_leave(schedule)


signals.connect_on( update_offsite_file, Offsite, post_save)

def generate_offsite_file(hour):

    job = os.path.join( settings.NIMBUS_JOBS_PATH, "offsite" )
    schedule = os.path.join( settings.NIMBUS_SCHEDULES_PATH, "offsite" )

    try:
        storage = Storage.objects.get(address="127.0.0.1")
    except Storage.DoesNotExist, error:
        logger = logging.getLogger(__name__)
        logger.error("Impossivel gerar job do offsite. Storage local nao existe")
        return 

    render_to_file( job,
                    "job",
                    name="Upload offsite",
                    schedule="offsite_schedule",
                    level="Incremental",
                    storage=storage.bacula_name(),
                    fileset="empty fileset",
                    priority=10,
                    client="empty client",
                    pool="empty pool",
                    offsite=True,
                    offsite_param="-u")


    render_to_file( schedule,
                    "schedule",
                    name="offsite_schedule",
                    runs=["daily at %s:%s" % (hour.hour, 
                                              hour.minute)])
    



