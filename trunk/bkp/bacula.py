import os
import datetime

class Bacula:
    WHERE_DEFAULT="/tmp/bacula-restore"

    def last_jobs(cls):
        """Returns list of dicts with  20 last jobs in overall system."""
        lastjobs_query =   ''' SELECT j.Name, jc.Name as "cName", j.Level, j.StartTime, j.EndTime,
                            j.JobFiles, j.JobBytes , JobErrors, JobStatus
                            FROM Job AS j INNER JOIN Client AS jc
                            ON j.ClientId = jc.ClientId;
                            LIMIT 20
                            '''
        return cls.dictfetch_query(lastjobs_query)
    last_jobs = classmethod(last_jobs)

    def running_jobs(cls):
        """Returns list of dicts with  10 running jobs in overall system."""
        runningjobs_query = ''' SELECT j.Name, jc.Name as "cName", j.Level, j.StartTime
                            FROM Job AS j INNER JOIN Client as jc ON j.ClientId = jc.ClientId
                            WHERE j.JobStatus = 'R' OR j.JobStatus = 'p' OR j.JobStatus = 'j'
                            OR j.JobStatus = 'c' OR j.JobStatus = 'd' OR j.JobStatus = 's'
                            OR j.JobStatus = 'M' OR j.JobStatus = 'm' OR j.JobStatus = 'S'
                            OR j.JobStatus = 'F' OR j.JobStatus = 'B'
                            LIMIT 10
                            '''
        return cls.dictfetch_query(runningjobs_query)
    running_jobs = classmethod(running_jobs)
                        
                        
    def db_size(cls):
        """Returns bacula's database size in MB."""
        dbsize_query =  ''' SELECT (sum(data_length+index_length )/(1024 * 1024)) AS "DBSIZE"
                        FROM information_schema.TABLES
                        WHERE table_schema = 'bacula'
                        GROUP BY table_schema
                        '''
        try:
            result = cls.dictfetch_query(dbsize_query)[0]['DBSIZE']
            return result
        except Exception:
            return ''
    db_size = classmethod(db_size)                
    
    def num_procedures(cls):
        """Returns generator of dict with number or total procedures stored at Nimbus."""
        numproc_query = '''SELECT count(*) AS "Procedures"
                        FROM backup_corporativo.bkp_procedure
                        '''
        try:
            result = cls.dictfetch_query(numproc_query)[0]['Procedures']
            return result
        except Exception:
            return ''
    num_procedures = classmethod(num_procedures)
                        
    def num_clients(cls):
        """Returns generator of dict with number of clients stored at Nimbus."""
        numcli_query =  '''SELECT count(*) AS "Computers"
                        FROM backup_corporativo.bkp_computer
                        '''
        try:
            result = cls.dictfetch_query(numcli_query)[0]['Computers']
            return result
        except Exception:
            return ''
    num_clients = classmethod(num_clients)
                        

    def total_mbytes(cls):
        """Returns generator of dict with total megabytes at bacula system backups."""
        totalbytes_query =  '''SELECT (sum(JobBytes)/(1024*1024)) AS "MBytes"
                            FROM Job WHERE Job.JobStatus = 'T';
                            '''    
        try:
            result = cls.dictfetch_query(totalbytes_query)[0]['MBytes']
            return result
        except Exception:
            return ''
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
