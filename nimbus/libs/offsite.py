#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from os.path import join, exists
import logging
from django.conf import settings
from datetime import datetime


import pycurl

from nimbus.offsite.models import Volume, UploadRequest, DownloadRequest
from nimbus.devices.models import Device
from nimbus.config.models import Config

from nimbusgateway import Api, File


DISK_LABELS_PATH = "/dev/disk/by-label/"


def list_disk_labels():
    try:
        return os.listdir(DISK_LABELS_PATH)
    except OSError, e:
        return []


def find_archive_devices():
    archives = [ dev.archive for dev in Device.objects.all() if dev.is_local ]
    return archives


def get_volume_abspath(volume, archives):
    for archive in archives:
        abspath = join( archive, volume )
        if exists( abspath ):
            return abspath


def get_volumes_abspath( volumes ):
    archives = find_archive_devices()
    return [ get_volume_abspath(volume, archives) for volume in volumes ]


def get_all_bacula_volumes():
    archives = find_archive_devices()
    volumes = []
    for arc in archives:
        files = os.listdir(arc)
        volumes.extend( join(arc, file) for file in files )
    return volumes



class BaseManager(object):
    
    def get_volume(self, volume_path ):
        volume, created = Volume.objects.get_or_create(path=volume_path)
        return volume
    
    def get_volumes(self, volumes_path=None ):

        if volumes_path:
            for path in volumes_path:
                self.get_volume(path)

        return Volume.objects.all()


    def create_upload_request(self, volume_path ):
        volume = self.get_volume(volume_path=volume_path)
        request, created = UploadRequest\
                            .objects.get_or_create(volume=volume)
        return request


    def create_download_request(self, volume_path ):
        volume = self.get_volume(volume_path=volume_path)
        request, created = DownloadRequest\
                            .objects.get_or_create(volume=volume)
        return request


    def get_upload_requests(self):
        return UploadRequest.objects.all()


    def get_download_requests(self):
        return DownloadRequest.objects.all()


    def upload_all_volumes(self):
        volumes = get_all_bacula_volumes()
        self.upload_volumes(volumes)


    def upload_volumes(self, volumes):
        volumes = get_volumes_abspath(volumes)
        for vol in volumes:
            self.create_upload_request(vol)
        self.process_pending_upload_requests()


    def download_all_volumes(self):
        volumes = self.get_remote_volumes_list()
        self.download_volumes(volumes)


    def download_volumes(self, volumes):
        for vol in volumes:
            self.create_download_request(vol)
        self.process_pending_download_requests()





class RemoteManager(BaseManager):

    MAX_RETRY = 3


    def __init__(self):
        settings = Config.get_instance()

        self.api = Api(username=settings.username,
                       password=settings.password,
                       gateway_url=settings.gateway_url)

        if settings.UPLOAD_RATE > 0:
            self.upload_rate = settings.offsite_upload_rate
        else:
            self.upload_rate = None


    def process_pending_upload_requests(self):
        requests = self.get_upload_requests()
        self.process_requests( requests, self.api.upload_file,
                               ratelimit=self.upload_rate)


    def get_remote_volumes_list(self):
        return [ f[0] for f in self.api.list_all_files() ]


    def process_pending_download_requests(self):
        requests = self.get_download_requests()
        self.process_requests( requests, self.api.download_file) 


    def process_requests( self, requests, process_function, 
                          limitrate=None):
        
        logger = logging.getLogger(__name__)

        for req in requests:
            req.last_attempt = datetime.now()

            retry = 0
            while retry < self.MAX_RETRY:
                try:
                    req.attempts += 1
                    req.save()
                    process_function(req.volume.path, req.volume.filename,
                                     limitrate=limitrate, callback=req.update)
                    req.finish()
                    logger.info("%s processado com sucesso" % req)
                    retry += 1
                    break
                except pycurl.error, e:
                    logger.error("Erro ao processar %s" % req)
                






class LocalManager(BaseManager):
    SIZE_512KB = 512 * 1024

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination


    def get_remote_volumes_list(self):
        files = [ join(self.origin, f) for f in os.listdir(self.origin) ]
        return filter( os.path.isfile, files)

    def process_pending_upload_requests(self):
        requests = self.get_upload_requests()
        self.process_requests( requests )


    def process_pending_download_requests(self):
        requests = self.get_download_requests()
        self.process_requests( requests ) 


    def process_requests( self, requests):
        
        logger = logging.getLogger(__name__)

        for req in requests:
            req.last_attempt = datetime.now()

            req.attempts += 1
            req.save()
            
            try:

                self._copy( req.volume.path, join(self.destination, 
                                                  req.volume.filename), 
                                                  req.update)

                req.finish()

                logger.info("%s processado com sucesso" % req)
            except Exception, e:
                logger.exception("Erro ao processar %s" % req)


    def _copy(self, origin, destination, callback):

        ori = File(origin, "rb", callback)
        dest = file(destination, "wb")

        while True:
            data = ori.read( self.SIZE_512KB )
            
            if not data:
                break

            dest.write(data)

        ori.close()
        dest.close()

                



