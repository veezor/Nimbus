#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import datetime
import tempfile

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
        self.logger.info("Executando reload no bacula")
        try:
            configcheck.check_baculadir(settings.BACULADIR_CONF)
            configcheck.check_bconsole(settings.BCONSOLE_CONF)
            output = self.cmd.reload.run()
            return output
        except configcheck.ConfigFileError, error:
            logging.exception("Arquivo de configuracao do bacula-sd gerado com erros")



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
    
    
  


