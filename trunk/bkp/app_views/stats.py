#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp.utils import *
from backup_corporativo.bkp.views import global_vars, require_authentication, authentication_required
# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


### Stats ###
@authentication_required
def view_stats(request):
    vars_dict, forms_dict, return_dict = global_vars(request)

    # TODO: remove following chunk of code from view!
    import MySQLdb
    runningjobs_query = ''' select j.Name, jc.Name, j.Level, j.StartTime, j.EndTime, \
                        j.JobFiles, j.JobBytes , JobErrors, JobStatus from Job as j \
                        INNER JOIN Client as jc on j.ClientId = jc.ClientId \
                        WHERE j.JobStatus = 'R' or j.JobStatus = 'p' or j.JobStatus = 'j' \
                        or j.JobStatus = 'c' or j.JobStatus = 'd' or j.JobStatus = 's' \
                        or j.JobStatus = 'M' or j.JobStatus = 'm' or j.JobStatus = 'S' \
                        or j.JobStatus = 'F' or j.JobStatus = 'B'; \
                        '''
    lastjobs_query =   ''' select j.Name, jc.Name, j.Level, j.StartTime, j.EndTime, \
                        j.JobFiles, j.JobBytes , JobErrors, JobStatus \
                        from Job as j INNER JOIN Client as jc \
                        on j.ClientId = jc.ClientId; \
                        '''
    dbsize_query =  ''' SELECT table_schema, 
                    sum( data_length + index_length ) / (1024 * 1024) "DBSIZE" \
                    FROM information_schema.TABLES \
                    WHERE table_schema = 'bacula' \
                    GROUP BY table_schema; \
                    '''
    numproc_query = '''select count(*) "Procedimentos" \
                    from backup_corporativo.bkp_procedure; \
                    '''
    numcli_query =  '''select count(*) "Computadores" \
                    from backup_corporativo.bkp_computer; \
                    '''
    totalbytes_query =  '''select sum(JobBytes) "Bytes" \
                        from Job where Job.JobStatus = 'T'; \
                        '''
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="mysqladmin", db="bacula")
        cursor = db.cursor()
        cursor.execute(runningjobs_query)
        vars_dict['runningjobs'] = cursor.fetchall()
        cursor.execute(lastjobs_query)
        vars_dict['lastjobs'] = cursor.fetchall()
        cursor.execute(dbsize_query)    
        vars_dict['dbsize'] = cursor.fetchall()[0][1]
        cursor.execute(numproc_query)
        vars_dict['numproc'] = int(cursor.fetchall()[0][0])
        cursor.execute(numcli_query)
        vars_dict['numcli'] = int(cursor.fetchall()[0][0])
        cursor.execute(totalbytes_query)
        vars_dict['tbytes'] = cursor.fetchall()[0][0]
    except:
        db = object()
    # Load forms and vars
    return_dict = merge_dicts(return_dict, forms_dict, vars_dict)
    return render_to_response('bkp/view/view_stats.html', return_dict, context_instance=RequestContext(request))
