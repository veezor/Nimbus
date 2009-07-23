#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime

class Bacula:
    WHERE_DEFAULT="/tmp/bacula-restore"

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
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_restore_last = classmethod(run_restore_last)
    
    def run_restore_date(cls, ClientName, Date,ClientRestore, Where, fileset_name):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" before="%(tg_date)s" fileset="%(fileset_name)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date,'fileset_name':fileset_name}
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_restore_date = classmethod(run_restore_date)
  
    def run_restore_jobid(cls, ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client="%(client_name)s" restoreclient="%(client_restore)s" select all done yes where="%(restore_path)s" jobid="%(job_id)s"\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
        BaculaLog.notice(["command: %s" % cmd])
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
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_backup = classmethod(run_backup)
    
    
    def dictfetch_query(cls, query):
        """Returns generator of dicts from given query executed."""
        from backup_corporativo.bkp.utils import dictfetch

        cursor = cls.db_query(query)
        return dictfetch(cursor)
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
            cursor.execute(query)
            db.commit()
        except ProgrammingError:
            raise Exception('Error na query %s')
        except Warning:
            pass
        finally:
            db.close()
        return cursor
    db_query = classmethod(db_query)
    
    
class BaculaLog:
    def notice(cls, msgs_list):
        import time
        try:
            log = cls.debug_log_file()
            for msg in msgs_list:
                log_entry = "%s [notice] - %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), msg)
                log.write(str(log_entry).encode("string-escape"))
                log.write("\n")
        except IOError:
            raise Exception("Error at open custom/bacula_logs/debug_log attempt.") 
        finally:
            log.close()
    notice = classmethod(notice)

    def debug_log_file(cls):
        from backup_corporativo.bkp.utils import prepare_to_write, mount_path, create_or_leave
        return prepare_to_write('debug_log','custom/bacula_logs/',mod="a")
    debug_log_file = classmethod(debug_log_file)
