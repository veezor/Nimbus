CLIENT_LAST_JOBS_RAW_QUERY =\
    '''
    SELECT DISTINCT JobID, Client.Name as cName, Job.Name, 
    Level, JobStatus, StartTime, (EndTime-StartTime) as Duration, 
    JobFiles, JobBytes, JobErrors, FileSet.FileSet 
    FROM Job INNER JOIN Client 
    ON Job.ClientId = Client.ClientId 
    INNER JOIN FileSet
    ON Job.FileSetID = FileSet.FileSetID 
    WHERE Client.Name = '%(client_name)s'
    ORDER BY EndTime DESC LIMIT 15
    '''

CLIENT_RUNNING_JOBS_RAW_QUERY =\
    '''
    SELECT Job.Name, Level, StartTime, (Now() - EndTime) AS Duration,
    JobFiles, JobBytes , JobErrors, JobStatus 
    FROM Job INNER JOIN Client 
    ON Job.ClientId = Client.ClientId
    WHERE Client.Name = '%(client_name)s'
    AND (JobStatus = 'R' OR JobStatus = 'p' OR JobStatus = 'j'
    OR JobStatus = 'c' OR JobStatus = 'd' OR JobStatus = 's'
    OR JobStatus = 'M' OR JobStatus = 'm' OR JobStatus = 'S'
    OR JobStatus = 'F' OR JobStatus = 'B')
    ORDER BY StartTime DESC
    LIMIT 5
    '''

CLIENT_STATUS_RAW_QUERY =\
    ''' 
    SELECT JobStatus
    FROM Job INNER JOIN Client 
    ON Job.ClientID = Client.ClientID
    WHERE Client.Name = '%(client_name)s' 
    ORDER BY Job.EndTime DESC LIMIT 1;
    '''


CLIENT_RESTORE_JOBS_RAW_QUERY =\
    '''
    SELECT DISTINCT JobId, Client.Name as cName, Job.Name,
    StartTime, JobFiles, JobBytes,
    JobErrors, FileSet.FileSet 
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    INNER JOIN FileSet
    ON Job.FileSetID = FileSet.FileSetID
    WHERE Client.Name = '%(client_name)s' 
    AND FileSet = '%(file_set)s'
    AND JobStatus = 'T'
    ORDER BY EndTime DESC LIMIT 15
    '''

CLIENT_LAST_FULL_RAW_QUERY =\
    '''
    SELECT JobId,StartTime
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    INNER JOIN FileSet
    ON Job.FileSetId = FileSet.FileSetId
    WHERE Client.Name='%(client_name)s'
    AND JobStatus='T' AND Job.Level='F' 
    AND StartTime < '%(start_time)s'
    AND FileSet.FileSet = '%(file_set)s'
    ORDER BY Job.StartTime DESC 
    LIMIT 1
    '''
   
CLIENT_DELTA_RAW_QUERY =\
    '''
    SELECT Job.JobId
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    INNER JOIN FileSet
    ON Job.FileSetId = FileSet.FileSetId
    WHERE Client.Name='%(client_name)s'  
    AND JobStatus='T' AND Job.Level='I' 
    AND StartTime <= '%(delta_end)s' 
    AND StartTime >= '%(delta_begin)s'
    AND FileSet.FileSet = '%(file_set)s'
    ORDER BY Job.StartTime DESC;
    '''

JOB_START_TIME_RAW_QUERY =\
    '''
    SELECT JobId,StartTime
    FROM Job
    WHERE JobId = '%s'
    LIMIT 1
    '''


FILE_TREE_RAW_QUERY =\
    '''
    SELECT Path.Path, Filename.Name
    FROM Job INNER JOIN FileSet
    ON Job.FileSetId = FileSet.FileSetId
    INNER JOIN File
    ON Job.JobId = File.JobId
    INNER JOIN Filename
    ON Filename.FileNameId = File.FileNameId
    INNER JOIN Path
    ON File.PathId = Path.PathId
    WHERE FileSet.FileSet='%(file_set)s'
    '''
    
LAST_JOBS_QUERY =\
    ''' 
    SELECT j.Name, jc.Name as "cName", j.Level, j.StartTime, j.EndTime,
    j.JobFiles, j.JobBytes , JobErrors, JobStatus
    FROM Job AS j INNER JOIN Client AS jc
    ON j.ClientId = jc.ClientId;
    LIMIT 20
    '''

RUNNING_JOBS_QUERY =\
    ''' 
    SELECT j.Name, jc.Name AS cName, j.Level, j.StartTime
    FROM Job AS j INNER JOIN Client as jc ON j.ClientId = jc.ClientId
    WHERE j.JobStatus = 'R' OR j.JobStatus = 'p' OR j.JobStatus = 'j'
    OR j.JobStatus = 'c' OR j.JobStatus = 'd' OR j.JobStatus = 's'
    OR j.JobStatus = 'M' OR j.JobStatus = 'm' OR j.JobStatus = 'S'
    OR j.JobStatus = 'F' OR j.JobStatus = 'B'
    LIMIT 10
    '''

DB_SIZE_RAW_QUERY =\
    ''' 
    SELECT (SUM(data_length+index_length)/(1024 * 1024)) AS DBSIZE
    FROM information_schema.TABLES
    WHERE table_schema = '%(bacula_db_name)s'
    GROUP BY table_schema
    '''
    

NUM_PROC_QUERY =\
    '''
    SELECT count(*) AS Procedures
    FROM backup_corporativo.bkp_procedure
    '''

NUM_CLI_QUERY =\
    '''
    SELECT count(*) AS Computers
    FROM backup_corporativo.bkp_computer
    '''

# TODO: fix formula since this is getting more than whats actually at HD
TOTAL_MBYTES_QUERY =\
    '''
    SELECT (sum(JobBytes)/(1024*1024)) AS MBytes
    FROM Job WHERE Job.JobStatus = 'T';
    '''