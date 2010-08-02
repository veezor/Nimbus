#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.db import connections
from django.db.models import Sum

from nimbus.shared import utils
from nimbus.bacula import models


import nimbus.shared.sqlqueries as sql 

import logging


import pybacula
from pybacula import BaculaCommandLine

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
        output = self.cmd.reload.run()
        return output


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


    def run_restore_last(self, client_name, client_restore=None, 
                         where=settings.RESTORE_POINT_DEFAULT):

        self.logger.info("Executando run_restore_last ")
        client_restore = client_restore if client_restore else client_name
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.current.all.done.yes.where[where].run()

    
    def run_restore_date(self, client_name, date, client_restore, where, fileset_name):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        self.logger.info("Executando run_restore_date ")
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.all.done.yes.where[where].before[date].\
                fileset[fileset_name].run()
  
    def run_restore_jobid(self, client_name, jobid, client_restore=None, 
                          where=settings.RESTORE_POINT_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        self.logger.info("Executando run_restore_jobid ")
        client_restore = client_restore if client_restore else client_name
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.all.done.yes.where[where].jobid[jobid].run()


    def run_restore(self, client_name, jobid=None, date=None, client_restore=None, 
                     where=settings.RESTORE_POINT_DEFAULT, fileset_name=None):
        """Method to restore a Job"""

        self.logger.info("Executando run_restore ")
        client_restore = client_restore if client_restore else client_name
        if fileset_name and date:
            return self.run_restore_date(client_name, date, client_restore, where, fileset_name)
        elif jobid:
            return self.run_restore_jobid(client_name, jobid, client_restore, where)
        elif not date and not jobid:
            return self.run_restore_last( client_name, client_restore, where)
        else:
            raise RestoreCallError("Invalid call of run_restore")
  

    def run_backup(self, job_name, level="Full", client_name=None, date=None):
        """ Date Format:  YYYY-MM-DD HH:MM:SS
            Level: Full/Incremental
        """
        self.logger.info("Executando run_backup ")
        if not date:
            sum_seconds = datetime.timedelta(seconds=10)
            now = datetime.datetime.now() + sum_seconds
            date = now.strftime("%Y-%m-%d %H:%M:%S")

        if client_name:
            return self.cmd.run.client[client_name].\
            job[job_name].level[level].when[date].yes.run()
        else:
            return self.cmd.run.\
            job[job_name].level[level].when[date].yes.run()
    
    
  


