#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import re
import MySQLdb as Database

from django.conf import settings
import django.db.backends as dbbackends 
from django.utils.safestring import SafeString, SafeUnicode

from nimbus.shared import utils
import nimbus.shared.sqlqueries as sql 

import logging
logger = logging.getLogger(__name__)

import pybacula
from pybacula import BaculaCommandLine

try:
    if settings.PYBACULA_TEST:
        pybacula.install_test_backend()
except AttributeError, e:
    pass






BCONSOLE_CONF = "/var/nimbus/custom/config/bconsole.conf"
RESTORE_POINT_DEFAULT = "/tmp/bacula-restore"


class RestoreCallError(Exception):
    pass

# TODO dividir funções de manipulação da console e de queries com banco de dados em duas classes distintas
class Bacula(object):

    def __init__(self):
        self.cmd = BaculaCommandLine(config=settings.BCONSOLE_CONF)
        self.baculadb = BaculaDatabase()


    def reload(self):
        logger.info("Executando reload no bacula")
        output = self.cmd.reload.run()
        return output


    def last_jobs(self):
        """Returns list of dicts with  20 last jobs in overall system."""
        cursor = self.baculadb.execute(sql.LAST_JOBS_QUERY)
        return utils.dictfetch(cursor)


    def running_jobs(self):
        """Returns list of dicts with  10 running jobs in overall system."""
        cursor = self.baculadb.execute(sql.RUNNING_JOBS_QUERY)
        return utils.dictfetch(cursor)


    def db_size(self):
        """Returns bacula's database size in MB."""
        dbsize_query = sql.DB_SIZE_RAW_QUERY % {'bacula_db_name': settings.BACULA_DATABASE_NAME}
        cursor = self.baculadb.execute(dbsize_query)
        result = cursor.fetchone()
        return result[0] if result else ''

    def num_procedures(self):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        cursor = self.baculadb.execute(sql.NUM_PROC_QUERY)
        result = cursor.fetchone()
        return result[0] if result else ''


    def num_clients(self):
        """Returns generator of dict with number of clients stored at Nimbus."""
        cursor = self.baculadb.execute(sql.NUM_CLI_QUERY)
        result = cursor.fetchone() 
        return result[0] if result else ''
                        
   
    def total_mbytes(self):
        """Returns generator of dict with total megabytes at bacula system backups."""
        cursor = self.baculadb.execute(sql.TOTAL_MBYTES_QUERY)
        result = cursor.fetchone()
        return result[0] if result else ''

    def run_restore_last(self, client_name, client_restore=None, where=RESTORE_POINT_DEFAULT):
        logger.info("Executando run_restore_last ")
        client_restore = client_restore if client_restore else client_name
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.current.all.done.yes.where[where].run()
    
    def run_restore_date(self, client_name, date, client_restore, where, fileset_name):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        logger.info("Executando run_restore_date ")
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.all.done.yes.where[where].before[date].\
                fileset[fileset_name].run()
  
    def run_restore_jobid(self, client_name, jobid, client_restore=None, where=RESTORE_POINT_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        logger.info("Executando run_restore_jobid ")
        client_restore = client_restore if client_restore else client_name
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.all.done.yes.where[where].jobid[jobid].run()


    def run_restore(self, client_name, jobid=None, date=None, client_restore=None, where=RESTORE_POINT_DEFAULT, fileset_name=None):
        """Method to restore a Job"""

        logger.info("Executando run_restore ")
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
        logger.info("Executando run_backup ")
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
    
    
  

# AVISO:
# essa classe foi apenas parcialmente implementada e contempla somente
# a execução de queries SQL puras através de seu método execute.
# Além do que foi descrito acima, seu funcionamento não é garantido
# para nenhum outro tipo de operação.
# Para maiores informações, consultar código original em: 
# http://djangoapi.quamquam.org/trunk/toc-django.db.backends.mysql-module.html
class BaculaDatabaseWrapper(dbbackends.BaseDatabaseWrapper):
    """Classe que encapsula operações básicas com banco de dados."""
    def __init__(self, **kwargs):
        super(BaculaDatabaseWrapper, self).__init__(**kwargs)
        self.server_version = None

    def _valid_connection(self):
        if self.connection is not None:
            try:
                self.connection.ping()
                return True
            except Database.DatabaseError, e:
                self.connection.close()
                self.connection = None
        return False
    
    def commit(self):
        self._commit()

    def cursor(self):
        return self._cursor()

    def _cursor(self):
        if not self._valid_connection():
            bacula_settings_dict['use_unicode'] = True
            self.connection = Database.connect(**bacula_settings_dict)
            self.connection.encoders[SafeUnicode] = self.connection.encoders[unicode]
            self.connection.encoders[SafeString] = self.connection.encoders[str]
        cursor = self.connection.cursor()
        return cursor


class BaculaDatabase(object):
    """Classe de fachada utilizada para gerenciar todas as conexões com a base de dados do bacula."""

    bacula_settings_dict = {
        'user': settings.BACULA_DATABASE_USER,
        'db': settings.BACULA_DATABASE_NAME,
        'passwd': settings.BACULA_DATABASE_PASSWORD,
        'host': settings.BACULA_DATABASE_HOST,
        'port': int(settings.BACULA_DATABASE_PORT)
    }

    wrapper = BaculaDatabaseWrapper(bacula_settings_dict) #highlander

    def cursor(self):
        return self.wrapper.cursor()
    
    def execute(self, query):
        try:
            cursor = self.cursor()
            cursor.execute(query)
            return cursor
        except Database.Warning:
            pass

    def commit(self):
        self.wrapper.commit()

