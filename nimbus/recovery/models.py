#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import bz2
import shutil
import logging
import tempfile
import datetime
from time import time


from django.conf import settings
from django.db import connections
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


from nimbus.offsite import managers as offsite
from nimbus.offsite import models as offsite_models
from nimbus.procedures.models import Procedure
from nimbus.security.exceptions import AdministrativeModelError
from nimbus.config import commands
from nimbus.shared import utils



def rewrite_nimbus_conf_files():
    shutil.rmtree(settings.NIMBUS_CUSTOM_DIR)
    commands.create_conf_dirs()
    app_labels = [name.split('.')[-1]\
                    for name in settings.INSTALLED_APPS\
                      if name.startswith('nimbus')]

    app_labels.remove('bacula')
    app_labels.remove('base')

    nimbus_models = [c.model_class() for c in ContentType.objects.filter(app_label__in=app_labels)]
    for model in nimbus_models:
        try:
            for instance in model.objects.all():
                try:
                    instance.save()
                except AdministrativeModelError:
                    instance.save(system_permission=True)
        except AttributeError:
            #sometimes filter returns a content-type as None
            pass



def recovery_nimbus(offsite_manager):
    logger = logging.getLogger(__name__)
    recovery_manager = RecoveryManager(offsite_manager)
    logger.info(_(u"Starting download databases"))
    recovery_manager.download_databases()
    logger.info(_(u"database download completed successfully"))
    # stop the world - nimbus,bacula,cron
    logger.info(_(u"Starting database recovery"))
    recovery_manager.recovery_databases()
    logger.info(_(u"database recovery completed successfully"))
    logger.info(_(u"Generating configuration files"))
    rewrite_nimbus_conf_files()
    logger.info(_(u"Configuration files generated successfully"))
    logger.info(_(u"Starting download backup files"))
    recovery_manager.download_volumes()
    logger.info(_(u"Download backup files completed"))
    # start the world - nimbus,bacula,cron
    recovery_manager.finish()


def recovery_nimbus_from_offsite():
    return recovery_nimbus(offsite.RemoteManager())




class RecoveryManager(object):

    def __init__(self, offsite_manager):
        self.offsite_manager = offsite_manager
        self.s3_volumes_cache = None


    def download_databases(self):
        nimbus_db = os.path.basename(offsite.NIMBUS_DUMP)
        bacula_db = os.path.basename(offsite.BACULA_DUMP)
        self.offsite_manager.create_download_request(nimbus_db)
        self.offsite_manager.create_download_request(bacula_db)
        self.offsite_manager.process_pending_download_requests()


    def _recovery_database(self, dbname, filename):


        bziped_filename = os.path.basename(filename)
        bziped_dumpfile = os.path.join(settings.NIMBUS_DEFAULT_ARCHIVE , bziped_filename)

        bziped = bz2.BZ2File(bziped_dumpfile)
        dump_filename = tempfile.mktemp()


        with file(dump_filename, 'w') as dump:
            while True:
                content = bziped.read(256 * 1024) #256kb
                if not content:
                    break
                dump.write(content)
        bziped.close()

        manager = utils.get_nimbus_manager()
        manager.recreate_db(dbname, dump_filename)




    def recovery_databases(self):

        for c in connections.all():
            c.close() # close all django db connections

        self._recovery_database( 'bacula', offsite.BACULA_DUMP)
        self._recovery_database( 'nimbus', offsite.NIMBUS_DUMP)


    def download_volumes(self):
        offsite_models.DownloadRequest.objects.all().delete() # clean up
        reporter = RecoveryProgressReporter(self.offsite_manager)


        for procedure, volumes in reporter:
            self.offsite_manager.download_volumes(volumes)


    def finish(self):
        self.offsite_manager.finish()



class TimedCallback(object):


    def __init__(self, callback, time):
        self.callback = callback
        self.time = time
        self.last_call = None


    def __call__(self, *args, **kwargs):
        if self.last_call is None:
            return self._call(*args, **kwargs)
        else:
            if time() - self.last_call > self.time:
                return self._call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        r = self.callback(*args, **kwargs)
        self.last_call = time()
        return r




class RecoveryProgressReporter(object):


    def __init__(self, remote_manager):
        self.remote_manager = remote_manager
        self.procedures = Procedure.objects.all()

        s3_volumes = self.remote_manager.get_remote_volumes()
        self.s3_volumes_cache = {}

        s3 = remote_manager.s3
        if s3.rate_limit is None:
            s3.callbacks.add_callback(s3.rate_limiter)
        s3.callbacks.add_callback(self.callback)


        for key in s3_volumes:
            self.s3_volumes_cache[key.name] = key

        for p in self.procedures:
            p.size_on_offsite = self._get_procedure_size_on_offsite(p)



    def _get_bytes_data(self):
        total_size = 0
        for p in self.procedures:
            total_size += p.size_on_offsite

        downloaded_size = 0
        for p in self.procedures:
            p.downloaded_size = self._get_downloaded_size_from_procedure(p)
            downloaded_size += p.downloaded_size

        bytes_remain = total_size - downloaded_size
        percent = (float(downloaded_size)/total_size)*100
        return total_size, downloaded_size, bytes_remain, int(percent)


    def _get_eta(self, rate, bytesr):
        kb = bytesr/1024.0
        if not rate is None and rate > 0:
            time = int(kb/rate)
            return str(datetime.timedelta(seconds=time))
        else:
            return _(u"stalled")


    def _get_offsite_volumes_from_procedure(self, procedure):
        volumes = procedure.volume_names
        keys = []

        for volume in volumes:
            try:
                keys.append( self.s3_volumes_cache[volume] )
            except KeyError:
                pass

        return keys


    def _get_procedure_size_on_offsite(self, procedure):
        keys = self._get_offsite_volumes_from_procedure(procedure)
        return sum( key.size for key in keys )


    def _get_downloaded_size_from_procedure(self, procedure):
        volumes = set(procedure.volume_names)
        local_volumes = offsite.get_all_bacula_volumes()

        size = 0

        for fullpath in local_volumes:
            filename = os.path.basename(fullpath)
            if filename in volumes:
                volume_size = os.path.getsize(fullpath)
                size += volume_size

        return size


    @property
    def callback(self):
        return TimedCallback(self._callback, 5.0)


    def _callback(self, transferred_size, total_size):
        (total_size, downloaded_size,
         bytes_remain, percent) = self._get_bytes_data()

        os.system("clear")
        print _("Nimbus Recovery")

        f = utils.filesizeformat

        for p in self.procedures:
            print _("{0} \t {1} of {2}").format(p.name,
                                          f(p.downloaded_size),
                                          f(p.size_on_offsite))


        rate = self.remote_manager.s3.rate_limiter.rate
        eta = self._get_eta(rate, bytes_remain)
        if rate is None:
            rate = 0
        rate = f(rate*1024)

        print _("Completed \t {0} of {1} - {2}% - Estimated time: {3}. Download rate: {4}/s").format(f(downloaded_size),
                                                                    f(total_size),
                                                                    percent,
                                                                    eta,
                                                                    rate)

    def __iter__(self):
        for p in self.procedures:
            volumes = [ vol.name for vol in self._get_offsite_volumes_from_procedure(p) ]
            yield (p, volumes)

