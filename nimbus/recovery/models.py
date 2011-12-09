#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import bz2
import shutil
import logging
import tempfile
import xmlrpclib
import subprocess


from django.conf import settings
from django.contrib.contenttypes.models import ContentType


from nimbus.offsite import managers as offsite
from nimbus.security.exceptions import AdministrativeModelError
from nimbus.config import commands



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
        for instance in model.objects.all():
            try:
                instance.save()
            except AdministrativeModelError:
                instance.save(system_permission=True)



def recovery_nimbus(offsite_manager):
    logger = logging.getLogger(__name__)
    logger.info("Parando os servicos")
    system_manager = xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
    system_manager.director_stop()
    system_manager.nimbus_stop()
    system_manager.ngninx_stop()


    recovery_manager = RecoveryManager(offsite_manager)
    logger.info("iniciando download da base de dados")
    recovery_manager.download_databases()
    logger.info("download da base de dados efetuado com sucesso")
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


    system_manager.nimbus_start()
    system_manager.ngninx_start()
    system_manager.director_start()



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


    def _recovery_database(self, filename, database):


        bziped_filename = os.path.basename(filename)
        bziped_dumpfile = os.path.join(settings.NIMBUS_DEFAULT_ARCHIVE , bziped_filename)
        db_data = settings.DATABASES['default']
        name = db_data['NAME']
        user = db_data['USER']
        password = db_data['PASSWORD']


        bziped = bz2.BZ2File(bziped_dumpfile)
        dump_filename = tempfile.mktemp()


        with file(dump_filename, 'w') as dump:
            while True:
                content = bziped.read(256 * 1024) #256kb
                if not content:
                    break
                dump.write(content)
        bziped.close()


        env = os.environ.copy()
        env['PGPASSWORD'] = password
        cmd = subprocess.Popen(["/usr/bin/psql",
                                "-U",user,
                                "-d",name,
                                "-f",dump_filename,
                                "--no-password"],
                                stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                env=env)
        cmd.communicate()

        if cmd.returncode != 0:
            raise subprocess.CalledProcessError()



    def recovery_databases(self):
        self._recovery_database( offsite.BACULA_DUMP, 'bacula')
        self.recovery_database( offsite.NIMBUS_DUMP,
                                'default')

    def download_volumes(self):
        self.offsite_manager.download_all_volumes()

    def finish(self):
        self.offsite_manager.finish()
