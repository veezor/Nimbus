import os
import datetime

class Bacula:
    WHERE_DEFAULT="/tmp/bacula-restore"


    # ClassMethods    
    def run_restore_last(cls, ClientName, ClientRestore="", Where=WHERE_DEFAULT):
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where}
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_restore_last = classmethod(run_restore_last)
    
    def run_restore_date(cls, ClientName, Date,ClientRestore="", Where=WHERE_DEFAULT):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s before=%(tg_date)s\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date}
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_restore_date = classmethod(run_restore_date)
  
    def run_restore_jobid(cls, ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        BCONSOLE_CONF = "/var/django/backup_corporativo/bkp/custom/config/bconsole.conf"
        cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select all done yes where=%(restore_path)s jobid=%(job_id)s\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_restore_jobid = classmethod(run_restore_jobid)

    def run_restore(cls, ClientName, JobId="", Date="", ClientRestore="", Where=WHERE_DEFAULT):
        """ClassMethod to restore a Job"""
        if ClientRestore == "":
            ClientRestore = ClientName
        elif JobId != "":
            cls.run_restore_jobid(ClientName,JobId,ClientRestore,Where)
        elif Date != "":
            cls.run_restore_date(ClientName,Date,ClientRestore,Where)
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
            cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrun job="%(job_name)s" level=%(job_level)s when="%(tg_date)s" yes\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'job_name':JobName, 'job_level':Level, 'tg_date':Date,'client_name':client_name}
        else:
            cmd = """bconsole -c%(bconsole_conf)s <<BACULAEOF \nrun job="%(job_name)s" level=%(job_level)s when="%(tg_date)s" yes\nBACULAEOF""" % {'bconsole_conf':BCONSOLE_CONF, 'job_name':JobName, 'job_level':Level, 'tg_date':Date}
        BaculaLog.notice(["command: %s" % cmd])
        os.system(cmd)
    run_backup = classmethod(run_backup)
    
    
    def dictfetch_query(cls, query):
        from backup_corporativo.bkp.utils import dictfetch

        cursor = cls.db_query(query)
        return dictfetch(cursor)
    dictfetch_query = classmethod(dictfetch_query)
    
    
    def db_query(cls, query):
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
        except:
            raise Exception('Error in connect to bacula database')
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
