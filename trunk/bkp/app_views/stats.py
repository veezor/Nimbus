#!/usr/bin/python
# -*- coding: utf-8 -*-

# Application
from backup_corporativo.bkp import utils
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
    from backup_corporativo.bkp.bacula import Bacula
    from SOAPpy import SOAPProxy
    server = SOAPProxy("http://127.0.0.1:8888")
    vars_dict['dir_status'] = server.status_director()
    vars_dict['sd_status'] = server.status_storage()
    vars_dict['fd_status'] = server.status_client()
    vars_dict['runningjobs'] = Bacula.running_jobs()
    vars_dict['lastjobs'] = Bacula.last_jobs()
    vars_dict['dbsize'] = Bacula.db_size()
    vars_dict['numproc'] = Bacula.num_procedures()
    vars_dict['numcli'] = Bacula.num_clients()
    vars_dict['tmbytes'] = Bacula.total_mbytes()
    return_dict = utils.merge_dicts(
        return_dict,
        forms_dict,
        vars_dict)
    return render_to_response(
        'bkp/stats/stats_jobs_history.html',
        return_dict,
        context_instance=RequestContext(request))