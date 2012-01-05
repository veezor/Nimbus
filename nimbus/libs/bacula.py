#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import datetime
import tempfile
import xmlrpclib

from django.conf import settings



import pybacula
from pybacula import BaculaCommandLine, configcheck, BConsoleInitError


from nimbus.shared import utils
from nimbus.bacula import models


try:
    if settings.PYBACULA_TEST:
        pybacula.install_test_backend()
except AttributeError, e:
    # TODO: Tratar
    pass


class Bacula(object):

    def __init__(self):
        self.cmd = BaculaCommandLine(config=settings.BCONSOLE_CONF)
        self.logger = logging.getLogger(__name__)

    def reload(self):
        if not bacula_is_locked():
            try:
                configcheck.check_baculadir(settings.BACULADIR_CONF)
                configcheck.check_bconsole(settings.BCONSOLE_CONF)
                output = self.cmd.reload.run()
                return output
            except configcheck.ConfigFileError, error:
                logger = logging.getLogger(__name__)
                logger.exception("Arquivo de configuracao do bacula-dir gerado com erros")

    def _get_items_from_bconsole_output(self, output):
        result = []
        for line in output.split("\n"):
            data = line.split("\t")
            if len(data) > 1:
                result.append(data[-1])
        result.sort()
        return result

    def list_files(self, jobid, path):
        result = []
        self.cmd._bvfs_update.run()
        dirs = self.cmd._bvfs_lsdir.jobid[jobid].path[path].run()
        dirs = self._get_items_from_bconsole_output(dirs)
        if '.' in dirs:
            dirs.remove('.')
        if '..' in dirs:
            dirs.remove('..')
        result.extend( dirs )
        files = self.cmd._bvfs_lsfiles.jobid[jobid].path[path].run()
        result.extend( self._get_items_from_bconsole_output(files) )
        result.sort()
        result = [ path + p.decode("utf-8") for p in result ]
        return result

    def run_restore(self, client_name, jobid, where, files):
        self.logger.info("Executando run_restore_")
        filename = tempfile.mktemp()
        for fname in list(files):
            if utils.isdir(fname):
                subfiles = models.File.objects\
                        .select_related()\
                        .filter(path__path__startswith=fname)
                files.extend( s.fullname for s in subfiles  )


        with file(filename, "w") as f:
            for fname in files:
                f.write( fname.encode("utf-8") + "\n" )
        
        return self.cmd.restore.\
                client[client_name].\
                file["<" + filename].\
                restoreclient[client_name].\
                select.all.done.yes.where[where].jobid[jobid].run()


    def run_backup(self, job_name, client_name):
        """ Date Format:  YYYY-MM-DD HH:MM:SS
            Level: Full/Incremental"""
        self.logger.info("Executando run_backup ")
        sum_seconds = datetime.timedelta(seconds=10)
        now = datetime.datetime.now() + sum_seconds
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        if client_name:
            return self.cmd.run.client[client_name].\
            job[job_name].yes.run()
            # job[job_name].level["Full"].when[date].yes.run()


    def cancel_procedure(self, procedure):
        self.cmd.cancel.job[procedure.bacula_name].run()
        for job_id in procedure.jobs_id_to_cancel:
            self.cmd.cancel.jobid[job_id].run()


    def purge_volumes(self, volumes, pool_name):
        purge = self.cmd.purge
        for volume in volumes:
            purge.volume[volume]
        purge.pool[pool_name]
        purge.run()

    def truncate_volumes(self, pool_name):
        self.cmd.purge.volume\
            .action["truncate"]\
            .pool[pool_name].run()

    def delete_pool(self, pool_name):
        self.cmd.delete.pool[pool_name].raw('\nyes').run()


def bacula_is_locked():
    return os.path.exists(settings.BACULA_LOCK_FILE)



def unlock_bacula_and_start():
    if bacula_is_locked():
        force_unlock_bacula_and_start()


def force_unlock_bacula_and_start():
    try:
        os.remove(settings.BACULA_LOCK_FILE)
    except OSError:
        pass #ignore
    try:
        logger = logging.getLogger(__name__)
        manager = xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
        stdout = manager.director_start()
        logger.info("bacula-dir started and unlocked")
        logger.info(stdout)
    except Exception, error:
        logger.exception("start bacula-dir error")




def lock_and_stop_bacula():
    if not bacula_is_locked():
        with file(settings.BACULA_LOCK_FILE, "w"):
            pass
        logger = logging.getLogger(__name__)
        try:
            manager = xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
            stdout = manager.director_stop()
            logger.info("bacula-dir stopped and locked")
            logger.info(stdout)
        except Exception, error:
            logger.exception("stop bacula-dir error")



class BaculaLock(object):

    def __enter__(self):
        lock_and_stop_bacula()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        unlock_bacula_and_start()






def _force_baculadir_restart():
    if not bacula_is_locked():
        try:
            logger = logging.getLogger(__name__)
            manager = xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
            stdout = manager.director_restart()
            logger.info("bacula-dir restart ok")
            logger.info(stdout)
        except Exception, error:
            logger.error("Reload bacula-dir error")



def call_reload_baculadir():
    try:
        logger = logging.getLogger(__name__)
        logger.info("Iniciando comunicacao com o bacula")
        bacula = Bacula()
        bacula.reload()
        logger.info("Reload no bacula executado com sucesso")
        del bacula
    except BConsoleInitError, e:
        logger.error("Comunicação com o bacula falhou, vou tentar o restart")
        _force_baculadir_restart()
        logger.error("Comunicação com o bacula falhou")



