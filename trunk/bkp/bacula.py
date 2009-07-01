import os
import datetime

class Bacula:
    WHERE_DEFAULT="/tmp/bacula-restore"

    def __run_restore_last(ClientName, ClientRestore="", Where=WHERE_DEFAULT):
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where}
        os.system(cmd)
    
    def __run_restore_date(ClientName, Date,ClientRestore="", Where=WHERE_DEFAULT):
        """Date Format:  YYYY-MM-DD HH:MM:SS ."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select current all done yes where=%(restore_path)s before=%(tg_date)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'tg_date':Date}
        os.system(cmd)
  
    def __run_restore_jobid(ClientName, JobId,ClientRestore="", Where=WHERE_DEFAULT):
        """JobId Format: specify a JobId or comma separated list of JobIds to be restored."""
        ClientRestore = ClientRestore and ClientRestore or ClientName
        cmd = "bconsole << BACULAEOF \nrestore client=%(client_name)s restoreclient=%(client_restore)s select all done yes where=%(restore_path)s jobid=%(job_id)s\nBACULAEOF" % {'client_name':ClientName, 'client_restore':ClientRestore, 'restore_path':Where, 'job_id':JobId}
        os.system(cmd)
    

    # ClassMethods    
    def run_restore(ClientName, JobId="", Date="", ClientRestore="", Where=WHERE_DEFAULT):
        """ClassMethod to restore a Job"""
        if ClientRestore == "":
            ClientRestore = ClientName
        elif JobId != "":
            __run_restore_jobid(ClientName,JobId,ClientRestore,Where)
        elif Date != "":
            __run_restore_date(ClientName,Date,ClientRestore,Where)
        elif Date == "" and JobId == "":
            __run_restore_last(ClientName,ClientRestore,Where)
        else:
            raise Exception("Invalid call of run_restore")
    run_restore = classmethod(run_restore)
   
    def run_backup(JobName, Level="Full", Date=""):
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