#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime

import MySQLdb as Database
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations, util
from django.utils.safestring import SafeString, SafeUnicode

import logging
from backup_corporativo.bkp import utils
from backup_corporativo import settings

logger = logging.getLogger(__name__)


# TODO dividir funções de manipulação da console e de queries com banco de dados em duas classes distintas
class Bacula:
    WHERE_DEFAULT = "/tmp/bacula-restore"
    BACULA_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"

    def client_status(cls,client_name):
        cmd =   """
                echo 'sta client=%(client_name)s'|bconsole -c %(bacula_conf)s|grep %(client_name)s
                """ % {'client_name':client_name, 'bacula_conf':BACULA_CONF}
        logger.info(cmd)
        ##NimbusLog.notice(category='bconsole', type='cmd', content=cmd) #TODO criar constantes para os tipos adequados
        output = os.popen(cmd).read()
        return output
    client_status = classmethod(client_status)


    def reload(cls):
        cmd =   """
                echo 'reload'|bconsole -c %(bacula_conf)s
                """ % {'bacula_conf':cls.BACULA_CONF}
        #NimbusLog.notice(category='bconsole', type='cmd', content=cmd) #TODO criar constantes para os tipos adequados
        logger.info(cmd)
        output = os.popen(cmd).read()
        return output
    reload = classmethod(reload)
    
    def messages(cls):
        cmd =   """
                echo 'm'|bconsole -c %(bacula_conf)s
                """ % {'bacula_conf':BACULA_CONF}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        output = os.popen(cmd).read()
        return output
    messages = classmethod(messages)

    def last_jobs(cls):
        """Returns list of dicts with  20 last jobs in overall system."""
        from backup_corporativo.bkp.sql_queries import LAST_JOBS_QUERY
        cursor = BaculaDatabase.execute(LAST_JOBS_QUERY)
        return utils.dictfetch(cursor)
    last_jobs = classmethod(last_jobs)

    def running_jobs(cls):
        """Returns list of dicts with  10 running jobs in overall system."""
        from backup_corporativo.bkp.sql_queries import RUNNING_JOBS_QUERY
        cursor = BaculaDatabase.execute(RUNNING_JOBS_QUERY)
        return utils.dictfetch(cursor)
    running_jobs = classmethod(running_jobs)
                        
    def db_size(cls):
        """Returns bacula's database size in MB."""
        from backup_corporativo.bkp.sql_queries import DB_SIZE_RAW_QUERY
        try:
            from backup_corporativo.settings import BACULA_DB_NAME
            dbsize_query = DB_SIZE_RAW_QUERY % {'bacula_db_name':BACULA_DB_NAME,}
            cursor = BaculaDatabase.execute(dbsize_query)
            result = cursor.fetchone()
            return result and result[0] or ''
        except ImportError:
            return ''
    db_size = classmethod(db_size)                
    
    # TODO mover código para local adequado
    def num_procedures(cls):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        from backup_corporativo.bkp.sql_queries import NUM_PROC_QUERY
        cursor = BaculaDatabase.execute(NUM_PROC_QUERY)
        result = cursor.fetchone()
        return result and result[0] or ''
    num_procedures = classmethod(num_procedures)
                        
    # TODO mover código para local adequado
    def num_clients(cls):
        """Returns generator of dict with number of clients stored at Nimbus."""
        from backup_corporativo.bkp.sql_queries import NUM_CLI_QUERY
        cursor = BaculaDatabase.execute(NUM_CLI_QUERY)
        result = cursor.fetchone() 
        return result and result[0] or ''
    num_clients = classmethod(num_clients)
                        
    def total_mbytes(cls):
        """Returns generator of dict with total megabytes at bacula system backups."""
        from backup_corporativo.bkp.sql_queries import TOTAL_MBYTES_QUERY
        cursor = BaculaDatabase.execute(TOTAL_MBYTES_QUERY)
        result = cursor.fetchone()
        return result and result[0] or ''
    total_mbytes = classmethod(total_mbytes)

    # ClassMethods
    # TODO: BCONSOLE_CONF declarar em algum lugar 
    # TODO: Otimizar pastas, corrigir caso para quando marcar só uma pasta.
    def tmp_restore(cls, client_from_restore, client_to_restore, date_to_restore, directory_to_restore, fileset_name, file_list):
        from backup_corporativo.bkp import utils
        import re
        folder_re = '[a-zA-Z0-9.:@_-]+/$'
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        raw_cmd = '''bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_from)s restoreclient=%(client_to)s select yes where=%(dir)s fileset=%(fileset)s before="%(date)s"\n'''
        for filepath in file_list:
            for item in filepath:
                if re.match(folder_re, item):
                    raw_cmd += 'cd %s\n' % item
                else:
                    raw_cmd += "mark %s\n" % item
                    raw_cmd += "cd /\n"
                    break
        raw_cmd += "done\n"
        raw_cmd += "\nBACULAEOF"
        cmd = raw_cmd % {'bconsole_conf':BCONSOLE_CONF,
                        'client_from':client_from_restore,
                        'client_to':client_to_restore,
                        'dir':directory_to_restore,
                        'fileset':fileset_name,
                        'date':date_to_restore,}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    tmp_restore = classmethod(tmp_restore)
        
    def run_restore_last(cls, ClientName, ClientRestore="", Where=WHERE_DEFAULT):
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_restore_last = classmethod(run_restore_last)
    
    def run_restore_date(cls, ClientName, Date,ClientRestore, Where, fileset_name):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" before="%(tg_date)s" fileset="%(fileset_name)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date,'fileset_name':fileset_name}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_restore_date = classmethod(run_restore_date)
  
    def run_restore_jobid(cls, ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" jobid="%(job_id)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_restore_jobid = classmethod(run_restore_jobid)

    def run_restore(cls, ClientName, JobId="", Date="", ClientRestore="", Where=WHERE_DEFAULT, fileset_name=""):
        """ClassMethod to restore a Job"""
        if ClientRestore == "":
            ClientRestore = ClientName
        if fileset_name and Date:
            cls.run_restore_date(ClientName,Date,ClientRestore,Where,fileset_name)
        elif JobId != "":
            cls.run_restore_jobid(ClientName,JobId,ClientRestore,Where)
        elif Date == "" and JobId == "":
            cls.run_restore_last(ClientName,ClientRestore,Where)
        else:
            raise Exception("Invalid call of run_restore")
    run_restore = classmethod(run_restore)
   
    def run_backup(cls, JobName, Level="Full", client_name="", Date=""):
        """ Date Format:  YYYY-MM-DD HH:MM:SS
            Level: Full/Incremental
        """
        if not Date:
            sum_seconds = datetime.timedelta(seconds=10)
            now = datetime.datetime.now() + sum_seconds
            Date = now.strftime("%Y-%m-%d %H:%M:%S")
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        if client_name:
            cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrun client="%(client_name)s" job="%(job_name)s" level="%(job_level)s" when="%(tg_date)s" yes\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'job_name':JobName, 'job_level':Level, 'tg_date':Date,'client_name':client_name}
        else:
            cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrun job="%(job_name)s" level="%(job_level)s" when="%(tg_date)s" yes\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'job_name':JobName, 'job_level':Level, 'tg_date':Date}
        #NimbusLog.notice(category='bconsole', type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_backup = classmethod(run_backup)
    
    
    def restore_files(cls, client_name, client_restore, restore_path, tg_date, fileset_name, files_dict):
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select yes where="%(restore_path)s" before="%(tg_date)s" fileset="%(fileset_name)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date,'fileset_name':fileset_name}
        for key in files_dict.keys():
            cmd.append("%()s\n" % {'value':files_dict[key]})
    restore_files = classmethod(restore_files)
   
# AVISO:
# essa classe foi apenas parcialmente implementada e contempla somente
# a execução de queries SQL puras através de seu método execute.
# Além do que foi descrito acima, seu funcionamento não é garantido para nenhum outro tipo de operação.
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

class BaculaDatabase:
    """Classe de fachada utilizada para gerenciar todas as conexões com a base de dados do bacula."""
    #ClassMethods
    def cursor(cls):
        b1 = BaculaDatabaseWrapper(settings_dict=utils.get_settings_dict())
        return b1.cursor()
    cursor = classmethod(cursor)
    
    def execute(cls, query):
        cursor = cls.cursor()
        #NimbusLog.notice(category='database', type='query',content=query) #TODO criar constantes para os tipos adequados
        try:
            cursor.execute(query)
            return cursor
        except Database.Warning:
            pass
    execute = classmethod(execute)
