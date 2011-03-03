#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import bz2
import subprocess
import time
from os.path import join, exists, isfile, isabs
import logging
from django.conf import settings
from datetime import datetime
import stat
from pwd import getpwnam


import pycurl

from devicemanager import StorageDeviceManager

from nimbus.base.models import UUIDBaseModel
from nimbus.storages.models import Device
from nimbus.offsite.models import Offsite
from nimbus.pools.models import Pool


from nimbus.offsite.models import ( Volume, 
                                    RemoteUploadRequest,
                                    LocalUploadRequest,
                                    DownloadRequest,
                                    UploadTransferredData,
                                    DownloadTransferredData,
                                    DeleteRequest)


from nimbusgateway import Api, File
from django.contrib.contenttypes.models import ContentType


DISK_LABELS_PATH = "/dev/disk/by-label/"
NIMBUS_DUMP = "/var/nimbus/nimbus-sql.bz2"
BACULA_DUMP = "/var/nimbus/bacula-sql.bz2"


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
        if exists( abspath ) and isfile( abspath ):
            return abspath


def get_volumes_abspath( volumes ):
    archives = find_archive_devices()
    return [ get_volume_abspath(volume, archives) for volume in volumes ]


def get_all_bacula_volumes():
    archives = find_archive_devices()
    volumes = []
    for arc in archives:

        files = os.listdir(arc)

        for filename in files:

            fullpath = join(arc, filename)

            if isfile( fullpath ):
                volumes.append( fullpath )

    return volumes



def register_transferred_data(request, initialbytes):
    bytes = request.transferred_bytes - initialbytes
    if isinstance(request, (RemoteUploadRequest, LocalUploadRequest)):
        UploadTransferredData.objects.create(bytes=bytes)
    else:
        DownloadTransferredData.objects.create(bytes=bytes)


def filename_is_volumename(filename):
    parts = filename.split("_")

    if len(parts) == 1:
        return False

    pool_name = parts[0]
    
    try:
        pool = Pool.objects.get(uuid__uuid_hex=pool_name)
        name = pool.uuid.uuid_hex + "_pool-vol-"
        return filename.startswith(name)
    except Pool.DoesNotExist, error:
        return False



def get_offsite_interface():
    config = Offsite.get_instance()
    api = Api(username=config.username,
              password=config.password,
              gateway_url=config.gateway_url)
    return api



class BaseManager(object):

    UploadRequestClass = RemoteUploadRequest
    DownloadRequestClass = DownloadRequest
    
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
        request, created = self.UploadRequestClass\
                            .objects.get_or_create(volume=volume)
        return request


    def create_download_request(self, volume_path ):
        volume = self.get_volume(volume_path=volume_path)
        request, created = self.DownloadRequestClass\
                            .objects.get_or_create(volume=volume)
        return request


    def get_upload_requests(self):
        return self.UploadRequestClass.objects.all().order_by('-created_at')


    def get_download_requests(self):
        return self.DownloadRequestClass.objects.all()


    def upload_all_volumes(self):
        volumes = get_all_bacula_volumes()
        self.upload_volumes(volumes)


    def upload_volumes(self, volumes):
        volumes = get_volumes_abspath(volumes)
        for vol in volumes:
            self.create_upload_request(vol)
        
        self.generate_database_dump_upload_request()
        self.process_pending_upload_requests()

    def generate_database_dump_upload_request(self):
        if exists(NIMBUS_DUMP):
            self.create_upload_request(NIMBUS_DUMP)
        if exists(BACULA_DUMP):
            self.create_upload_request(BACULA_DUMP)


    def download_all_volumes(self):
        volumes = self.get_remote_volumes_list()
        self.download_volumes(volumes)


    def download_volumes(self, volumes):
        for vol in volumes:
            self.create_download_request(vol)
        self.process_pending_download_requests()


    def create_delete_request(self, volume_path ):
        volume = self.get_volume(volume_path=volume_path)
        request, created = DeleteRequest\
                            .objects.get_or_create(volume=volume)
        return request


    def create_deletes_request(self, volumes):
        for volume in volumes:
            self.create_delete_request(volume)


    def delete_volume(self, volume):
        raise AttributeError("method not implemented")



    def delete_volumes(self, volumes):
        for volume in volumes:
            self.delete_volume(volume)


    def process_pending_delete_requests(self):
        for delete_request in DeleteRequest.objects.all():
            self.delete_volume(delete_request.volume.path)






class RemoteManager(BaseManager):

    MAX_RETRY = 3


    def __init__(self):
        settings = Offsite.get_instance()

        self.api = Api(username=settings.username,
                       password=settings.password,
                       gateway_url=settings.gateway_url)

        if settings.upload_rate > 0:
            self.upload_rate = settings.upload_rate
        else:
            self.upload_rate = None


    def process_pending_upload_requests(self):
        requests = self.get_upload_requests()
        self.process_requests( requests, self.api.upload_file,
                               ratelimit=self.upload_rate)


    def get_remote_volumes_list(self):
        return [ f[0] for f in self.api.list_all_files() if filename_is_volumename(f[0]) ]


    def _download_file(self, filename, dest, 
                       ratelimit=None, callback=None):
        device = Device.objects.all()[0]

        if isabs(filename):
            destfilename = filename
        else:
            destfilename = join(device.archive, filename)

        self.api.download_file( filename, destfilename,
                                ratelimit, callback, True)


        os.chmod( destfilename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        os.chown( destfilename, getpwnam("nimbus").pw_uid, getpwnam("bacula").pw_gid)


    def process_pending_download_requests(self):
        requests = self.get_download_requests()
        self.process_requests( requests, self._download_file) 


    def process_requests( self, requests, process_function, 
                          ratelimit=None):
        
        logger = logging.getLogger(__name__)

        for req in requests:
            req.last_attempt = datetime.now()

            retry = 0
            while retry < self.MAX_RETRY:
                try:
                    req.attempts += 1
                    req.last_update = time.time()

                    if isinstance(req, self.UploadRequestClass): # no resume
                        req.transferred_bytes = 0

                    initialbytes = req.transferred_bytes

                    req.save()
                    process_function(req.volume.path, req.volume.filename,
                                     ratelimit=ratelimit, callback=req.update)

                    req.finish()
                    logger.info("%s processado com sucesso" % req)
                    break
                except pycurl.error, e:
                    retry += 1
                    register_transferred_data(req, initialbytes)
                    logger.error("Erro ao processar %s" % req)


    def delete_volume(self, volume):
        try:
            self.api.delete_file(volume)
            DeleteRequest.objects.filter(volume__path=volume).delete()
        except pycurl.error, error:
            pass



                






class LocalManager(BaseManager):
    SIZE_512KB = 512 * 1024

    UploadRequestClass = LocalUploadRequest

    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination


    def get_remote_volumes_list(self):
        allfiles = os.listdir(self.origin)
        volume_files = [ f for f in allfiles if filename_is_volumename(f) ]
        files = [ join(self.origin, f) for f in volume_files ]
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


        try:
            os.chmod( destination, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
            os.chown( destination, getpwnam("nimbus").pw_uid, getpwnam("bacula").pw_gid)
        except (OSError, IOError), error:
            pass

        ori.close()
        dest.close()




class RecoveryManager(object):


    def __init__(self, manager):
        self.manager = manager



    def upload_databases(self):
        self.manager.create_upload_request(NIMBUS_DUMP)
        self.manager.create_upload_request(BACULA_DUMP)
        self.manager.process_pending_upload_requests()

    def download_databases(self):
        nimbus_db = os.path.split(NIMBUS_DUMP)[-1]
        bacula_db = os.path.split(BACULA_DUMP)[-1]
        self.manager.create_download_request(nimbus_db)
        self.manager.create_download_request(bacula_db)
        self.manager.process_pending_download_requests()


    def recovery_database(self, dumpfile, name, user, password):

        fileobj = bz2.BZ2File(dumpfile)
        content = fileobj.read()
        fileobj.close()

        cmd = subprocess.Popen(["/usr/bin/mysql",
                                "-u" + user,
                                "-p" + password,
                                "-D" + name ],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        cmd.communicate(content)


    def recovery_nimbus_dabatase(self):
        nimbus_file = NIMBUS_DUMP
        db_data = settings.DATABASES['default']
        self.recovery_database( nimbus_file,
                                db_data['NAME'],
                                db_data['USER'],
                                db_data['PASSWORD'])

    def recovery_bacula_dabatase(self):
        bacula_file = BACULA_DUMP
        db_data = settings.DATABASES['bacula']
        self.recovery_database( bacula_file,
                                db_data['NAME'],
                                db_data['USER'],
                                db_data['PASSWORD'])



    def recovery_databases(self):
        self.recovery_bacula_dabatase()
        self.recovery_nimbus_dabatase()


    def generate_conf_files(self):
        app_labels = [ name.split('.')[-1]\
                       for name in settings.INSTALLED_APPS\
                           if name.startswith('nimbus')]


        app_labels.remove('bacula')
        app_labels.remove('base')

        nimbus_models = [ c.model_class() for c in ContentType.objects.filter(app_label__in=app_labels) ]

        for model in nimbus_models:
            for instance in model.objects.all():
                if isinstance(instance, UUIDBaseModel): 
                    instance.save(system_permission=True)
                else:
                    instance.save()


    def download_volumes(self):
        self.manager.download_all_volumes()

    def finish(self):
        if isinstance(self.manager, LocalManager):
            storage = StorageDeviceManager( self.manager.device )
            storage.umount()
 
                
