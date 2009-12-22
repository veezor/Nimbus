#!/usr/bin/python
# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
import socket

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from environment import ENV

from backup_corporativo.bkp.bacula import Bacula
from backup_corporativo.bkp import utils
from backup_corporativo.bkp.views import global_vars, authentication_required


### Stats ###
@authentication_required
def main_statistics(request):
    E = ENV(request)
    
    if request.method == 'GET':
        try:
            server = ServerProxy("http://127.0.0.1:8888")
            E.dir_status = server.status_director()
            E.sd_status = server.status_storage()
            E.fd_status = server.status_client()
            #TODO: consertar estatísticas
            #E.dbsize = Bacula.db_size()
            #E.numproc = Bacula.num_procedures()
            #E.numcli = Bacula.num_clients()
            #E.tmbytes = Bacula.total_mbytes()
            E.template = 'bkp/stats/main_statistics.html'
        except socket.error, e:
            E.template = 'bkp/base.html'
        finally:
            return E.render()
    

@authentication_required
def history_statistics(request):
    E = ENV(request)
    
    if request.method == 'GET':
        try:
            server = ServerProxy("http://127.0.0.1:8888")
            #TODO: consertar estatísticas
            #E.runningjobs = Bacula.running_jobs()
            #E.lastjobs = Bacula.last_jobs()
            E.template = 'bkp/stats/history_statistics.html'
        except socket.error, e:
            E.template = 'bkp/base.html'
        finally:
            return E.render()
