import os
import datetime

class Bacula:
    WHERE_DEFAULT="/tmp/bacula-restore"

    # ClassMethods    
    def run_restore_last(cls, ClientName, ClientRestore="", Where=WHERE_DEFAULT):
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where}
        os.system(cmd)
    run_restore_last = classmethod(run_restore_last)
    
    def run_restore_date(cls, ClientName, Date,ClientRestore="", Where=WHERE_DEFAULT):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s before=%(tg_date)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date}
        os.system(cmd)
    run_restore_date = classmethod(run_restore_date)
  
    def run_restore_jobid(cls, ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select all done yes where=%(restore_path)s jobid=%(job_id)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
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
   
    def run_backup(cls, JobName, Level="Full", Date=""):
        """ Date Format:  YYYY-MM-DD HH:MM:SS
            Level: Full/Incremental
        """
        if not Date:
            sum_seconds = datetime.timedelta(seconds=10)
            now = datetime.datetime.now() + sum_seconds
            Date = now.strftime("%Y-%m-%d %H:%M:%S")
        cmd = "bconsole << BACULAEOF \nrun job=%(job_name)s level=%(job_level)s when=%(tg_date)s yes\nBACULAEOF" % {'job_name':JobName, 'job_level':Level, 'tg_date':Date}
        os.system(cmd)
    run_backup = classmethod(run_backup)
    
    def db_query(cls, query):
        import MySQLdb
        from backup_corporativo.bkp.utils import dictfetch
    	from backup_corporativo.settings import DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD
    	try:
    	    from backup_corporativo.settings import BACULA_DB_NAME
    	except:
    	    raise('Could not import BACULA_DB_NAME from settings.py')

        try:
            db = MySQLdb.connect(host=DATABASE_HOST, user=DATABASE_USER, passwd=DATABASE_PASSWORD, db=BACULA_DB_NAME)
            cursor = db.cursor()
            cursor.execute(query)
            result = dictfetch(cursor)
        except:
            raise Exception('Error in connect to bacula database')
        return result
    db_query = classmethod(db_query)