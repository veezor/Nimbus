#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
from backup_corporativo.bkp.models import NimbusLog

class Bacula:
    WHERE_DEFAULT = "/tmp/bacula-restore"
    BACULA_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"

    def client_status(cls,client_name):
        cmd =   """
                echo 'sta client=%(client_name)s'|bconsole -c %(bacula_conf)s|grep %(client_name)s
                """ % {'client_name':client_name, 'bacula_conf':BACULA_CONF}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        output = os.popen(cmd).read()
        return output
    client_status = classmethod(client_status)
        
        
    def reload(cls):
        cmd =   """
                echo 'reload'|bconsole -c %(bacula_conf)s
                """ % {'bacula_conf':cls.BACULA_CONF}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        output = os.popen(cmd).read()
        return output
    reload = classmethod(reload)
    
    
    
    def messages(cls):
        cmd =   """
                echo 'm'|bconsole -c %(bacula_conf)s
                """ % {'bacula_conf':BACULA_CONF}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        output = os.popen(cmd).read()
        return output
    messages = classmethod(messages)



    def last_jobs(cls):
        """Returns list of dicts with  20 last jobs in overall system."""
        from backup_corporativo.bkp.sql_queries import LAST_JOBS_QUERY
        return cls.dictfetch_query(LAST_JOBS_QUERY)
    last_jobs = classmethod(last_jobs)

    def running_jobs(cls):
        """Returns list of dicts with  10 running jobs in overall system."""
        from backup_corporativo.bkp.sql_queries import RUNNING_JOBS_QUERY
        return cls.dictfetch_query(RUNNING_JOBS_QUERY)
    running_jobs = classmethod(running_jobs)
                        
                        
    def db_size(cls):
        """Returns bacula's database size in MB."""
        from backup_corporativo.bkp.sql_queries import DB_SIZE_RAW_QUERY
        try:
            from backup_corporativo.settings import BACULA_DB_NAME
        except:
            raise Exception('Não foi possível importar BACULA_DB_NAME do settings.py')
        dbsize_query = DB_SIZE_RAW_QUERY % {'bacula_db_name':BACULA_DB_NAME,}
        result = cls.dictfetch_query(dbsize_query)
        result = result and result[0]['DBSIZE'] or ''
        return result
    db_size = classmethod(db_size)                
    
    def num_procedures(cls):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        from backup_corporativo.bkp.sql_queries import NUM_PROC_QUERY
        result = cls.dictfetch_query(NUM_PROC_QUERY)
        result = result and result[0]['Procedures'] or ''
        return result
    num_procedures = classmethod(num_procedures)
                        
    def num_clients(cls):
        """Returns generator of dict with number of clients stored at Nimbus."""
        from backup_corporativo.bkp.sql_queries import NUM_CLI_QUERY
        result = cls.dictfetch_query(NUM_CLI_QUERY)
        result = result and result[0]['Computers'] or ''
        return result
    num_clients = classmethod(num_clients)
                        
    def total_mbytes(cls):
        """Returns generator of dict with total megabytes at bacula system backups."""
        from backup_corporativo.bkp.sql_queries import TOTAL_MBYTES_QUERY
        result = cls.dictfetch_query(TOTAL_MBYTES_QUERY)
        result = result and result[0]['MBytes'] or ''
        return result
    total_mbytes = classmethod(total_mbytes)

    # ClassMethods    
    def run_restore_last(cls, ClientName, ClientRestore="", Where=WHERE_DEFAULT):
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_restore_last = classmethod(run_restore_last)
    
    def run_restore_date(cls, ClientName, Date,ClientRestore, Where, fileset_name):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" before="%(tg_date)s" fileset="%(fileset_name)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date,'fileset_name':fileset_name}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_restore_date = classmethod(run_restore_date)
  
    def run_restore_jobid(cls, ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" jobid="%(job_id)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
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
        cls.notice(type='cmd',content=cmd) #TODO criar constantes para os tipos adequados
        os.system(cmd)
    run_backup = classmethod(run_backup)
    
    
    def restore_files(cls, client_name, client_restore, restore_path, tg_date, fileset_name, files_dict):
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select yes where="%(restore_path)s" before="%(tg_date)s" fileset="%(fileset_name)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date,'fileset_name':fileset_name}
        for key in files_dict.keys():
            cmd.append("%()s\n" % {'value':files_dict[key]})
    restore_files = classmethod(restore_files)


    def dictfetch_query(cls, query, count_rows=False):
        """
        Returns generator of dicts from given query executed.
        If count_rows is set to True, will return cursor.rowcount as well.
        """
        from backup_corporativo.bkp.utils import dictfetch

        cursor = cls.db_query(query)
        return count_rows and (cursor.rowcount,dictfetch(cursor)) or dictfetch(cursor)
    dictfetch_query = classmethod(dictfetch_query)
    
    
    def db_query(cls, query):
        """Returns unfetched cursor with the given query executed."""
        from MySQLdb import ProgrammingError
        import MySQLdb
    	from backup_corporativo.settings import DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD
    	try:
    	    from backup_corporativo.settings import BACULA_DB_NAME
    	except:
    	    raise Exception('Could not import BACULA_DB_NAME from settings.py')

        try:
            db = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, passwd=DATABASE_PASSWORD, db=BACULA_DB_NAME)
            cursor = db.cursor()
            cls.notice(type='query',content=query) #TODO criar constantes para os tipos adequados
            cursor.execute(query)
            db.commit()
        except Warning:
            pass
        except ProgrammingError, e:
            raise Exception('Erro na query: %s' % e)
        finally:
            db.close()
        return cursor
    db_query = classmethod(db_query)
    
    def notice(cls, type, content):
        n1 = NimbusLog()
        n1.entry_category = 'bacula'
        n1.entry_type = type
        n1.entry_content = content
        n1.save()
    notice = classmethod(notice)