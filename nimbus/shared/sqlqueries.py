from django.conf import settings

LAST_SUCCESS_DATE_RAW_QUERY =\
    '''
    SELECT Level, EndTime
    FROM Job
    WHERE Name = '%(procedure_name)s' AND JobStatus = 'T'
    ORDER BY EndTime DESC LIMIT 1;    
    '''

CLIENT_SUCCESSFUL_JOBS_RAW_QUERY =\
    '''
    SELECT DISTINCT JobID, Client.Name as cName, Job.Name,
    Level, JobStatus, StartTime, (EndTime-StartTime) as Duration,
    JobFiles, JobBytes, JobErrors, FileSet.FileSet
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    INNER JOIN FileSet
    ON Job.FileSetID = FileSet.FileSetID
    WHERE Client.Name = '%(client_name)s'
    AND Job.JobStatus in ('T','W')
    ORDER BY EndTime DESC LIMIT 15
    '''

CLIENT_UNSUCCESSFUL_JOBS_RAW_QUERY =\
    '''
    SELECT DISTINCT JobID, Client.Name as cName, Job.Name,
    Level, JobStatus, StartTime, (EndTime-StartTime) as Duration,
    JobFiles, JobBytes, JobErrors, FileSet.FileSet
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    INNER JOIN FileSet
    ON Job.FileSetID = FileSet.FileSetID
    WHERE Client.Name = '%(client_name)s'
    AND Job.JobStatus in ('E','e','f','I')
    ORDER BY EndTime DESC
    '''

CLIENT_RUNNING_JOBS_RAW_QUERY =\
    '''
    SELECT Job.Name, Level, StartTime, (Now() - StartTime) AS Duration,
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
    StartTime, JobFiles, JobBytes, Job.Level,
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


   
LAST_JOBS_QUERY =\
    ''' 
    SELECT j.Name, jc.Name as "cName", j.Level, j.StartTime, j.EndTime,
    j.JobFiles, j.JobBytes , JobErrors, JobStatus
    FROM Job AS j INNER JOIN Client AS jc
    ON j.ClientId = jc.ClientId
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
    WHERE table_schema = %s
    GROUP BY table_schema
    LIMIT 1
    '''

NUM_PROC_QUERY =\
    '''
    SELECT count(*) AS Procedures
    FROM %s.bkp_procedure
    LIMIT 1
    ''' % settings.DATABASE_NAME

NUM_CLI_QUERY =\
    '''
    SELECT count(*) AS Computers
    FROM %s.bkp_computer
    LIMIT 1
    ''' % settings.DATABASE_NAME

# TODO: fix formula since this is getting more than whats actually at HD
TOTAL_MBYTES_QUERY =\
    '''
    SELECT (sum(JobBytes)/(1024*1024)) AS MBytes
    FROM Job WHERE Job.JobStatus = 'T'
    LIMIT 1
    '''
    
CLIENT_ID_RAW_QUERY =\
    '''
    SELECT ClientId FROM Client
    WHERE Client.Name = '%(client_name)s'
    LIMIT 1
    '''

# Restore Section
CREATE_TEMP1_QUERY =\
    '''
    CREATE TABLE temp1 (
    JobId BIGINT NOT NULL,
    JobTDate BIGINT
    )
    '''

TEMP1_TDATE_QUERY =\
    '''
    SELECT JobId, JobTDate
    FROM temp1
    LIMIT 1
    '''
CREATE_TEMP_QUERY =\
    '''
    CREATE TABLE temp (
    JobId BIGINT NOT NULL,
    JobTDate BIGINT,
    ClientId BIGINT NOT NULL,
    Level CHAR NOT NULL, 
    JobFiles INTEGER,
    JobBytes BIGINT,
    StartTime DATETIME,
    VolumeName VARCHAR(128) NOT NULL,
    StartFile INTEGER,
    VolSessionId INTEGER,
    VolSessionTime INTEGER
    )
    '''

DROP_TABLE_RAW_QUERY =\
    '''
    DROP TABLE IF EXISTS `%(table_name)s`
    '''


#OLD_CLIENT_LAST_FULL_RAW_QUERY =\
#    '''
#    SELECT JobId,StartTime
#    FROM Job INNER JOIN Client
#    ON Job.ClientId = Client.ClientId
#    INNER JOIN FileSet
#    ON Job.FileSetId = FileSet.FileSetId
#    WHERE Client.Name='%(client_name)s'
#    AND JobStatus='T' AND Job.Level='F' 
#    AND StartTime < '%(start_time)s'
#    AND FileSet.FileSet = '%(file_set)s'
#    ORDER BY Job.StartTime DESC 
#    LIMIT 1
#    '''

LOAD_FULL_RAW_QUERY =\
    '''
    INSERT INTO temp1
    SELECT Job.JobId,JobTdate
    FROM Job
    WHERE JobId = %(jid)s
    LIMIT 1
    '''
    
LOAD_LAST_FULL_RAW_QUERY =\
    '''
    INSERT INTO temp1
    SELECT Job.JobId,JobTdate
    FROM Client,Job,JobMedia,Media,FileSet
    WHERE Client.ClientId = %(client_id)s
    AND Job.ClientId = %(client_id)s
    AND Job.StartTime < '%(start_time)s'
    AND Level = 'F'
    AND JobStatus IN ('T','W')
    AND Type = 'B'
    AND JobMedia.JobId = Job.JobId
    AND Media.Enabled = 1
    AND JobMedia.MediaId = Media.MediaId
    AND Job.FileSetId = FileSet.FileSetId
    AND FileSet.FileSet = '%(fileset)s'
    ORDER BY Job.JobTDate DESC
    LIMIT 1;
    '''

LOAD_FULL_MEDIA_INFO_QUERY =\
    '''
    INSERT INTO temp
    SELECT Job.JobId,Job.JobTDate,Job.ClientId,
    Job.Level,Job.JobFiles,Job.JobBytes,StartTime,
    VolumeName,JobMedia.StartFile,VolSessionId,
    VolSessionTime 
    FROM temp1,Job,JobMedia,Media 
    WHERE temp1.JobId = Job.JobId 
    AND Level =  'F' 
    AND JobStatus IN ('T','W')
    AND Type = 'B' 
    AND Media.Enabled = 1 
    AND JobMedia.JobId = Job.JobId 
    AND JobMedia.MediaId = Media.MediaId
    '''

#OLD_CLIENT_DELTA_RAW_QUERY =\
#    '''
#    SELECT Job.JobId
#    FROM Job INNER JOIN Client
#    ON Job.ClientId = Client.ClientId
#    INNER JOIN FileSet
#    ON Job.FileSetId = FileSet.FileSetId
#    WHERE Client.Name='%(client_name)s'  
#    AND JobStatus='T' 
#    AND (Job.Level='I' OR Job.Level='F')
#    AND StartTime <= '%(delta_end)s' 
#    AND StartTime >= '%(delta_begin)s'
#    AND FileSet.FileSet = '%(file_set)s'
#    ORDER BY Job.StartTime DESC;
#    '''

LOAD_INC_MEDIA_INFO_RAW_QUERY =\
    '''
    INSERT INTO temp 
    SELECT Job.JobId,Job.JobTDate,Job.ClientId,
    Job.Level,Job.JobFiles,Job.JobBytes,Job.StartTime,
    Media.VolumeName,JobMedia.StartFile,Job.VolSessionId,
    Job.VolSessionTime 
    FROM Job,JobMedia,Media,FileSet 
    WHERE Job.JobTDate > '%(tdate)s'
    AND Job.StartTime <= '%(start_time)s'
    AND Job.ClientId = '%(client_id)s'
    AND Media.Enabled = 1 
    AND JobMedia.JobId = Job.JobId 
    AND JobMedia.MediaId = Media.MediaId 
    AND Job.Level = 'I' 
    AND JobStatus IN ('T','W') 
    AND Type = 'B' 
    AND Job.FileSetId = FileSet.FileSetId 
    AND FileSet.FileSet = '%(fileset)s'
    '''
    
JOBS_FOR_RESTORE_QUERY =\
    '''
    SELECT DISTINCT JobId,StartTime 
    FROM temp 
    ORDER BY StartTime ASC
    '''

#OLD_JOB_START_TIME_RAW_QUERY =\    
JOB_INFO_RAW_QUERY =\
    '''
    SELECT JobId,StartTime,Level
    FROM Job
    WHERE JobId = '%(job_id)s'
    LIMIT 1
    '''

JOB_STAT_RAW_QUERY =\
    '''
    SELECT JobBytes,RealEndTime
    FROM Job
    WHERE Name = '%(name)s'
    AND JobStatus in ('T', 'W')
    ORDER BY RealEndTime
    '''

JOB_STAT_GET_N_LAST_WITH_NAME = \
    '''
    SELECT JobBytes,RealEndTime 
    FROM Job 
    WHERE Name = '%(name)s' AND JobStatus in ('T', 'W')
    ORDER BY RealEndTime DESC 
    LIMIT %(size)d
    '''

JOB_STAT_GET_N_LAST = \
    '''
    SELECT JobBytes,RealEndTime 
    FROM Job 
    WHERE  JobStatus in ('T', 'W') 
    ORDER BY RealEndTime DESC 
    LIMIT %(size)d
    '''

JOB_STAT_GET_N_LAST_FROM_CLIENT = \
    '''
    SELECT DISTINCT JobBytes, RealEndTime
    FROM Job INNER JOIN Client
    ON Job.ClientId = Client.ClientId
    WHERE Client.Name = '%(client_name)s'
    AND Job.JobStatus in ('T','W')
    ORDER BY RealEndTime DESC LIMIT %(size)d
    '''



#OLD_FILE_TREE_RAW_QUERY =\
#    '''
#    SELECT Path.Path, Filename.Name
#    FROM File INNER JOIN Filename
#    ON Filename.FileNameId = File.FileNameId
#    INNER JOIN Path
#    ON File.PathId = Path.PathId
#    WHERE
#    '''

FILE_TREE_RAW_QUERY =\
    '''
    SELECT File.FileId as FId, Path.Path as FPath, Filename.Name as FName,
    File.FileIndex, File.JobId AS FJobId, File.LStat 
    FROM 
    (SELECT max(FileId) as FileId, PathId, FilenameId 
    FROM (SELECT FileId, PathId, FilenameId 
    FROM File 
    WHERE JobId IN (%(ids)s)) AS F 
    GROUP BY PathId, FilenameId) AS Temp 
    JOIN Filename 
    ON (Filename.FilenameId = Temp.FilenameId) 
    JOIN Path 
    ON (Path.PathId = Temp.PathId) 
    JOIN File 
    ON (File.FileId = Temp.FileId) 
    WHERE File.FileIndex > 0 
    ORDER BY JobId, FileIndex ASC
    '''

FILES_QUERY =\
    '''
    SELECT DISTINCT CONCAT(Path.Path,Filename.Name) 
    FROM File, Path, Filename 
    WHERE Filename.FilenameId = File.FilenameId 
    AND Path.PathId = File.PathId 
    AND File.JobId in (%s)
    AND File.FileIndex > 0 
    GROUP BY Path.Path, Filename.Name 
    ORDER BY File.JobID, File.FileIndex
    '''

FILES_BY_NIVEL_QUERY =\
    '''
    SELECT DISTINCT 
        SUBSTRING_INDEX(CONCAT(Path.Path,Filename.Name), '/', %d) ,
        SUBSTRING_INDEX(SUBSTRING_INDEX(CONCAT(Path.Path,Filename.Name) , '/', %d)  , '/', -1),
        IF (STRCMP(RIGHT(SUBSTRING_INDEX(CONCAT(Path.Path,Filename.Name), '/', %d),1), '/'), 0, 1)
    FROM File, Path, Filename 
    WHERE Filename.FilenameId = File.FilenameId 
    AND Path.PathId = File.PathId 
    AND File.JobId in (%s)
    AND File.FileIndex > 0 
    GROUP BY Path.Path, Filename.Name 
    ORDER BY File.JobID, File.FileIndex
    '''

PATHDEPTH_FUNCTION = """\
delimiter ||
DROP FUNCTION IF EXISTS PathDepth||
CREATE FUNCTION PathDepth(x VARCHAR(255)) RETURNS TINYINT(3) UNSIGNED LANGUAGE SQL NOT DETERMINISTIC READS SQL DATA
BEGIN
DECLARE count TINYINT(3) UNSIGNED;


SET count = (length(x)-length(REPLACE(x, '/', '')));
IF RIGHT(x, 1) = '/' THEN
    set count = count - 1;
END IF;

RETURN count;
END;

||
delimiter ;
"""


SELECT_FILES_FROM_JOB_PATH_DEPTH = """\
    SELECT DISTINCT Concat(Path.Path, Filename.Name) fullpath
    from File, Path, Filename 
    where File.PathId  = Path.PathId and 
    File.FilenameId = Filename.FilenameId and
    File.JobId = %s
    HAVING fullpath REGEXP %s and
    PathDepth(fullpath) = %s;

    """


SELECT_MORE_FILES_FROM_JOB_PATH_DEPTH = """\
    SELECT DISTINCT Concat(Path.Path, Filename.Name) fullpath
    from File, Path, Filename 
    where File.PathId  = Path.PathId and 
    File.FilenameId = Filename.FilenameId and
    File.JobId = %s
    HAVING fullpath NOT LIKE %s and
    PathDepth(fullpath) = %s;
    """





SELECT_FILES_FROM_PATTERN = """\
    SELECT DISTINCT Concat(Path.Path, Filename.Name) fullpath
    from File, Path, Filename 
    where File.PathId  = Path.PathId and 
    File.FilenameId = Filename.FilenameId and
    File.JobId = %s and
    Concat(Path.Path, Filename.Name) LIKE %s;
    """


SELECT_MIN_FILES_DEPTH = """\
    SELECT min(PathDepth(Concat(Path.Path, Filename.Name)))
    from File, Path, Filename 
    where File.PathId  = Path.PathId and 
    File.FilenameId = Filename.FilenameId and
    File.JobId = %s;
    """

SELECT_NEXT_FILES_DEPTH = """\
    SELECT MIN(S.depth) FROM 
        (SELECT PathDepth(Concat(Path.Path, Filename.Name)) depth 
            from File, Path, Filename 
            where File.PathId  = Path.PathId and 
            File.FilenameId = Filename.FilenameId and 
            File.JobId = %s having depth > %s) AS S;
    """


SELECT_NEXT_FILES_ON_DEPTH = """\
    SELECT MIN(S.depth) FROM 
        (SELECT PathDepth(Concat(Path.Path, Filename.Name)) depth 
            from File, Path, Filename 
            where File.PathId  = Path.PathId and 
            File.FilenameId = Filename.FilenameId and 
            Concat(Path.Path, Filename.Name) NOT LIKE %s and
            File.JobId = %s having depth > %s) AS S;
    """
