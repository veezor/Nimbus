#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
import re
import MySQLdb as Database

from django.conf import settings
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations, util
from django.utils.safestring import SafeString, SafeUnicode

from backup_corporativo.bkp import utils
from backup_corporativo.settings import BACULA_DATABASE_NAME
from backup_corporativo.bkp.sql_queries import LAST_JOBS_QUERY, RUNNING_JOBS_QUERY, DB_SIZE_RAW_QUERY, NUM_PROC_QUERY, NUM_CLI_QUERY, TOTAL_MBYTES_QUERY
from backup_corporativo.bkp import utils
from backup_corporativo import settings

import logging
logger = logging.getLogger(__name__)

import pybacula

try:
    if settings.PYBACULA_TEST:
        pybacula.test()
except AttributeError, e:
    pass



from pybacula import BaculaCommandLine


BCONSOLE_CONF = "/var/nimbus/custom/config/bconsole.conf"
WHERE_DEFAULT = "/tmp/bacula-restore"


class RestoreCallError(Exception):
    pass

# TODO dividir funções de manipulação da console e de queries com banco de dados em duas classes distintas
class Bacula(object):

    def __init__(self):
        self.cmd = BaculaCommandLine(config=BCONSOLE_CONF)
        self.baculadb = BaculaDatabase()


    def reload(self):
        logger.info("Executando reload no bacula")
        output = self.cmd.reload.run()
        return output


    def last_jobs(self):
        """Returns list of dicts with  20 last jobs in overall system."""
        cursor = self.baculadb.execute(LAST_JOBS_QUERY)
        return utils.dictfetch(cursor)


    def running_jobs(self):
        """Returns list of dicts with  10 running jobs in overall system."""
        cursor = self.baculadb.execute(RUNNING_JOBS_QUERY)
        return utils.dictfetch(cursor)


    def db_size(self):
        """Returns bacula's database size in MB."""
        dbsize_query = DB_SIZE_RAW_QUERY % {'bacula_db_name': settings.BACULA_DATABASE_NAME}
        cursor = self.baculadb.execute(dbsize_query)
        result = cursor.fetchone()
        return result[0] if result else ''

    # TODO mover código para local adequado
    def num_procedures(self):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        cursor = self.baculadb.execute(NUM_PROC_QUERY)
        result = cursor.fetchone()
        return result[0] if result else ''


    # TODO mover código para local adequado
    def num_clients(self):
        """Returns generator of dict with number of clients stored at Nimbus."""
        cursor = self.baculadb.execute(NUM_CLI_QUERY)
        result = cursor.fetchone() 
        return result[0] if result else ''
                        
   
    def total_mbytes(self):
        """Returns generator of dict with total megabytes at bacula system backups."""
        cursor = self.baculadb.execute(TOTAL_MBYTES_QUERY)
        result = cursor.fetchone()
        return result[0] if result else ''

    # ClassMethods
    # TODO: Otimizar pastas, corrigir caso para quando marcar só uma pasta.
    def tmp_restore(self, client_from_restore, client_to_restore, date_to_restore, directory_to_restore, fileset_name, file_list):
        logger.info("Executando tmp_restore")
        
        folder_re = '[a-zA-Z0-9.:@_-]+/$'

        restore = self.cmd.restore
        restore.client[client_from_restore].\
                restoreclient[client_to_restore].\
                select.yes.where[directory_to_restore].\
                fileset[fileset_name].\
                before[date_to_restore].run()
        cmd_list = []
        previous_folder = None
        for filepath in file_list:
            for item in filepath:
                if re.match(folder_re, item):
                    cmd_list.append('cd %s' % item)
                    previous_folder = item
                elif item == '':
                    cmd_list.append("cd ..")
                    cmd_list.append("mark %s" % previous_folder)
                    cmd_list.append("cd /")
                    previous_folder = None
                    break
                else:
                    cmd_list.append("mark %s" % item)
                    cmd_list.append("cd /\n")
                    previous_folder = None
                    break
        cmd_list.append("done")

        for cmd in cmd_list:
            r = restore.raw(cmd).run()
#   
    def run_restore_last(self, client_name, client_restore=None, where=WHERE_DEFAULT):
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
  
    def run_restore_jobid(self, client_name, jobid, client_restore=None, where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        logger.info("Executando run_restore_jobid ")
        client_restore = client_restore if client_restore else client_name
        return self.cmd.restore.\
                client[client_name].\
                restoreclient[client_restore].\
                select.all.done.yes.where[where].jobid[jobid].run()


    def run_restore(self, client_name, jobid=None, date=None, client_restore=None, where=WHERE_DEFAULT, fileset_name=None):
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
class BaculaDatabaseWrapper(BaseDatabaseWrapper):
    """Classe que encapsula operações básicas com banco de dados."""
    def __init__(self, **kwargs):
        super(BaculaDatabaseWrapper, self).__init__(**kwargs)
        self.server_version = None

    def _valid_connection(self):
        if self.connection is not None:
            try:
                self.connection.ping()
                return True
            except DatabaseError:
                self.connection.close()
                self.connection = None
        return False
    
    def commit(self):
        self._commit()

    def cursor(self):
        return self._cursor()

    def _cursor(self):
        if not self._valid_connection():
            bacula_settings_dict = dict()
            convert_dict = {'user': 'BACULA_DATABASE_USER',
                            'db': 'BACULA_DATABASE_NAME',
                            'passwd': 'BACULA_DATABASE_PASSWORD',
                            'host': 'BACULA_DATABASE_HOST',
                            'port': 'BACULA_DATABASE_PORT',}
            for key, value in convert_dict.items():
                content = self.settings_dict[value]
                if content:
                    if key in ('port',):
                        content = int(content)
                    bacula_settings_dict[key] = content
            
            bacula_settings_dict['use_unicode'] = True
            
            self.connection = Database.connect(**bacula_settings_dict)
            self.connection.encoders[SafeUnicode] = self.connection.encoders[unicode]
            self.connection.encoders[SafeString] = self.connection.encoders[str]
        cursor = self.connection.cursor()
        return cursor


class BaculaDatabase(object):
    """Classe de fachada utilizada para gerenciar todas as conexões com a base de dados do bacula."""

    def __init__(self):
        self.wrapper = BaculaDatabaseWrapper(settings_dict=utils.get_settings_dict())

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

