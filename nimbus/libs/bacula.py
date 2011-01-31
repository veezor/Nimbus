#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import datetime
import tempfile
import xmlrpclib

from django.conf import settings
from django.db import connections
from django.db.models import Sum

import pybacula
from pybacula import BaculaCommandLine, configcheck

from nimbus.shared import utils
from nimbus.bacula import models
import nimbus.shared.sqlqueries as sql 






try:
    if settings.PYBACULA_TEST:
        pybacula.install_test_backend()
except AttributeError, e:
    pass



class RestoreCallError(Exception):
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



    def db_size(self):
        """Returns bacula's database size in MB."""
        cursor = connections['bacula'].cursor()
        return cursor.execute(sql.DB_SIZE_RAW_QUERY, 
                                [settings.DATABASES['bacula']['NAME']])

    def num_procedures(self):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        from nimbus.procedures.models import Procedure
        return Procedure.objects.count()


    def num_clients(self):
        """Returns generator of dict with number of clients stored at Nimbus."""
        from nimbus.computers.models import Computer
        return Computer.objects.count()
                        
   
    def total_mbytes(self):
        """Returns generator of dict with total megabytes at bacula system backups."""
        r = models.Job.objects.filter(jobstatus='T').aggregate(sum=Sum('jobbytes'))
        return utils.bytes_to_mb(r['sum'])


 
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
                f.write( fname + "\n" )

        return self.cmd.restore.\
                client[client_name].\
                file["<" + filename].\
                restoreclient[client_name].\
                select.all.done.yes.where[where].jobid[jobid].run()



    def run_backup(self, job_name, client_name):
        """ Date Format:  YYYY-MM-DD HH:MM:SS
            Level: Full/Incremental
        """
        self.logger.info("Executando run_backup ")

        sum_seconds = datetime.timedelta(seconds=10)
        now = datetime.datetime.now() + sum_seconds
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        if client_name:
            return self.cmd.run.client[client_name].\
            job[job_name].level["Full"].when[date].yes.run()


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
        self.cmd.delete.pool[pool_name].run()
    
    
  

def bacula_is_locked():
    return os.path.exists(settings.BACULA_LOCK_FILE)




def unlock_bacula_and_start():

    if bacula_is_locked():
        os.remove(settings.BACULA_LOCK_FILE)

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

