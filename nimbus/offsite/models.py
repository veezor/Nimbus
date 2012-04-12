#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import json
import logging
import urllib2
from time import time
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save

#from nimbus.offsite import managers
from nimbus.offsite.S3 import S3, S3AuthError, MIN_MULTIPART_SIZE
from nimbus.bacula.models import Media, JobMedia
from nimbus.shared import fields, signals
# from nimbus.graphics.models import BaseGraphicData
from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.base.models import BaseModel as TheRealBaseModel
from nimbus.procedures.models import Procedure



class Offsite(BaseModel):
    AMZ_S3_HOST = "s3.amazonaws.com"

    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    access_key = models.CharField(max_length=255, blank=True, 
                                  null=True, editable=False)
    secret_key = models.CharField(max_length=255, blank=True, 
                                  null=True, editable=False)
    rate_limit = models.IntegerField(default=-1)
    plan_size = models.BigIntegerField(default=0, editable=False)
    host = models.CharField(max_length=255, blank=True, null=True, editable=False)
    active = models.BooleanField()



    class Meta:
        verbose_name = u"Configurações do offsite"

    @classmethod
    def on_remove(cls, procedure):
        from nimbus.offsite import managers
        from nimbus.offsite import queue_service

        remote_manager = managers.RemoteManager()

        pool_name = procedure.pool_bacula_name()
        medias = Media.objects.filter(pool__name=pool_name).distinct()
        volumes = [m.volumename for m in medias]

        remote_manager.create_deletes_request(volumes)
        queue_service_manager = queue_service.get_queue_service_manager()
        queue_service_manager.run_delete_agent()


    def clean(self):
        if self.active:

            logger = logging.getLogger(__name__)

            try:
                nimbus_central_data = self._get_nimbus_central_data()
                if nimbus_central_data['status'] != 1:
                    logger.error("Status da conta do usuário inválido")
                    raise ValidationError("Sua assinatura está com problemas, verifique situação na central de atendimento")
            except urllib2.HTTPError, error:
                if error.getcode() == 401:
                    logger.error("Username or password error")
                    raise ValidationError("Usuário ou senha incorretos")
                else:
                    logger.exception("Offsite test config")
                    raise ValidationError("Impossível conectar. Tente novamente mais tarde")
            except urllib2.URLError, error:
                    logger.exception("Offsite test config")
                    raise ValidationError("Erro, verifique sua conexão com a rede externa")




            self.plan_size = nimbus_central_data['quota']
            self.access_key = nimbus_central_data['accesskey']['id']
            self.secret_key = nimbus_central_data['accesskey']['secret']
            if nimbus_central_data.has_key('host'):
                self.host = nimbus_central_data['host']
            else:
                self.host = "s3.amazonaws.com"

            try:
                s3 = S3(username=self.username,
                        access_key=self.access_key,
                        secret_key=self.secret_key,
                        rate_limit=self.rate_limit,
                        host=self.host)
            except S3AuthError, error:
                logger.exception("nimbus central keys error")
                raise ValidationError("Erro de configuração. Contactar o suporte. Chaves não conferem")



    def _get_nimbus_central_data(self):

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        url = settings.NIMBUS_CENTRAL_USER_DATA_URL
        password_mgr.add_password(None, url, self.username, self.password)

        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)

        content = opener.open(url)
        data = content.read()
        content.close()
        return json.loads(data)
    

    @classmethod
    def get_s3_interface(cls):
        config = cls.get_instance()
        
        
        if config.rate_limit == -1:
            rate_limit = None
        else:
            rate_limit = config.rate_limit
        s3 = S3(username=config.username,
                 access_key=config.access_key,
                 secret_key=config.secret_key,
                 rate_limit=rate_limit,
                 host=config.host)

        return s3
    
class Volume(models.Model):

    path = fields.ModelPathField(max_length=2048, null=False)
    size = models.BigIntegerField(null=False, editable=False, default=0)

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
    transferred_bytes = models.BigIntegerField(default=0, editable=False)
    rate = models.IntegerField(default=0, editable=False)


    @property
    def procedure(self):
        return self.job.procedure


    @property
    def job(self):
        try:
            job_media = JobMedia.objects.filter(media__volumename=self.volume.filename)[0]
        except IndexError:
            return Procedure.objects.get(id=1).all_my_jobs[0]
        return job_media.job


    def reset_transferred_bytes(self):
        self.transferred_bytes = 0
        self.save()

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
        if not self.rate:
            return "stalled"
        time = self.remaining_bytes / self.rate
        hours,seconds = divmod(time, self.HOURS)
        minutes,seconds = divmod(seconds, self.MINUTES)
        return "%dh%dm%ds" % (hours, minutes, seconds)


    @property
    def finished_percent(self):
        if not self.volume.size:
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
    part = models.IntegerField(default=0, editable=False)


    def increment_part(self, filename, part):
        if ((part+1) * MIN_MULTIPART_SIZE) < self.volume.size:
            self.part = part + 1
            self.save()


    def reset_transferred_bytes(self):
        self.transferred_bytes = self.part * MIN_MULTIPART_SIZE
        self.save()


    def update(self, new_bytes_size, total_bytes):
        new_bytes_size = (self.part * MIN_MULTIPART_SIZE) + new_bytes_size
        super(RemoteUploadRequest, self).update(new_bytes_size, total_bytes)


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
    bytes = models.BigIntegerField(null=False)
    date = models.DateTimeField(null=False, default=datetime.now)

    class Meta:
        abstract = True


class UploadTransferredData( TransferredData ):
    # WTF
    pass


class DownloadTransferredData( TransferredData ):
    # WTF
    pass


def update_offsite(offsite):
    #Criando objeto JobTask
    from nimbus.procedures.models import JobTask
    task_objects = JobTask.objects.filter(name="Offsite").all()
    if (len(task_objects) == 0) and (offsite.active == True):
        task = JobTask()
        task.name = "Offsite"
        task.creator = offsite
        task.description = "Mantém uma cópia de seu backup na nuvem"
        task.command = "%s --upload-requests %%v" % settings.NIMBUS_EXE
        task.runswhen = "After"
        task.save()
        from nimbus.procedures.models import Procedure # loop
        try:
            procedure = Procedure.objects.get(id=1) # self backup
            procedure.job_tasks.add(task)
            procedure.save(system_permission=True)
        except Procedure.DoesNotExist, error:
            pass

    elif len(task_objects) > 0:
        if task_objects[0].active != offsite.active:
            task_objects[0].active = offsite.active
            task_objects[0].save()

def is_active():
    offsite = Offsite.get_instance()
    return offsite.active

class OffsiteGraphicsData(TheRealBaseModel):

    total = models.BigIntegerField(default=0, editable=False)
    used = models.BigIntegerField(default=0, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s de %s (%.2f%%)" % (self.timestamp.strftime("%H:%M:%S %d/%m/%Y"),
                                           self.used, self.total,
                                           (self.used*100/self.total))

def update_pool_size(procedure):
    offsite_conf = Offsite.get_instance()
    if offsite_conf.active and offsite_conf.host != offsite_conf.AMZ_S3_HOST:
        procedure.pool_size = settings.DEFAULT_PROCEDURE_POOL_SIZE # TODO: change model field to integer
    else:
        procedure.pool_size = 0



signals.connect_on(update_offsite, Offsite, post_save)
signals.connect_on( update_pool_size, Procedure, pre_save)
