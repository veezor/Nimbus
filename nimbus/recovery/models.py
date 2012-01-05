#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import bz2
import shutil
import logging
import tempfile
import subprocess


from django.conf import settings
from django.db import connections
from django.contrib.contenttypes.models import ContentType


from nimbus.offsite import managers as offsite
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
    logger.info("iniciando download da base de dados")
    recovery_manager.download_databases()
    logger.info("download da base de dados efetuado com sucesso")
    # stop the world
    logger.info("iniciando recuperacao da base de dados")
    recovery_manager.recovery_databases()
    logger.info("recuperacao da base de dados efetuado com sucesso")
    logger.info("iniciando geracao de arquivos de configuracao")
    rewrite_nimbus_conf_files()
    logger.info("geracao dos arquivos de configuracao realizada com sucesso")
    logger.info("iniciando download dos volumes")
    recovery_manager.download_volumes()
    logger.info("download dos volumes efetuado com sucesso")
    recovery_manager.finish()


def recovery_nimbus_from_offsite():
    return recovery_nimbus(offsite.RemoteManager())



class RecoveryManager(object):

    def __init__(self, offsite_manager):
        self.offsite_manager = offsite_manager


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
        self.offsite_manager.download_all_volumes()

    def finish(self):
        self.offsite_manager.finish()
