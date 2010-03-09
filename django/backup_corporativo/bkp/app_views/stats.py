#!/usr/bin/python
# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy
import socket

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response


import os


from environment import ENV

from backup_corporativo.bkp.bacula import Bacula, BaculaDatabase
from backup_corporativo.bkp import utils, models
from backup_corporativo.bkp.views import global_vars, authentication_required
from backup_corporativo.bkp.statistics import ( generate_computer_graph, 
                                                generate_procedure_graph,
                                                generate_jobs_graph, 
                                                update_diskusage_graph )


IMAGENS_URL = "/static/imagens/"
DEFAULT_IMG = "/static/imagens/none.png"
DISK_IMG = IMAGENS_URL + "disk.png"
JOBS_IMG = IMAGENS_URL + "jobs.png"




 ## Stats ###
@authentication_required
def main_statistics(request):
    return HttpResponseRedirect(utils.reverse('stats_global'))



@authentication_required
def stats_computer(request):
    E = ENV(request)

    if request.method == 'GET':
        computers = models.Computer.objects.all()
        E.imagens_url = IMAGENS_URL
        E.default_img = DEFAULT_IMG

        has_imagens = [ generate_computer_graph(computer) for computer in computers ]

        E.data = zip(computers, has_imagens)

        E.template = 'bkp/stats/stats_computer.html'
        return E.render()



@authentication_required
def stats_procedure(request):
    E = ENV(request)

    if request.method == 'GET':
        procedures = models.Procedure.objects.all()

        E.imagens_url = IMAGENS_URL
        E.default_img = DEFAULT_IMG

        has_imagens = [ generate_procedure_graph(procedure) for procedure in procedures ]
        E.data = zip(procedures, has_imagens)

        E.template = 'bkp/stats/stats_procedure.html'
        return E.render()



@authentication_required
def stats_global(request):
    E = ENV(request)

    if request.method == 'GET':

        try:
            bacula = Bacula()
            E.dbsize = bacula.db_size()
            E.numproc = bacula.num_procedures()
            E.numcli = bacula.num_clients()
            E.tmbytes = bacula.total_mbytes()


            server = ServerProxy("http://127.0.0.1:8888")
            E.dir_status = server.status_director()
            E.sd_status = server.status_storage()
            E.fd_status = server.status_client()
            #TODO: consertar estatísticas
        except socket.error, e:
            E.dir_status = "Director não responde"
            E.sd_status = "Storage não responde"
            E.fd_status = "Client não responde"


        update_diskusage_graph()
        generate_jobs_graph()
        E.template = 'bkp/stats/stats_global.html'
        E.disk_img = DISK_IMG
        E.jobs_img = JOBS_IMG
        return E.render()





#### Stats ###
#@authentication_required
#def main_statistics(request):
#    E = ENV(request)
#    
#    if request.method == 'GET':
#        try:
#            server = ServerProxy("http://127.0.0.1:8888")
#            E.dir_status = server.status_director()
#            E.sd_status = server.status_storage()
#            E.fd_status = server.status_client()
#            #TODO: consertar estatísticas
#            #E.dbsize = Bacula.db_size()
#            #E.numproc = Bacula.num_procedures()
#            #E.numcli = Bacula.num_clients()
#            #E.tmbytes = Bacula.total_mbytes()
#            E.template = 'bkp/stats/main_statistics.html'
#        except socket.error, e:
#            E.dir_status = "Error"
#            E.sd_status = "Error"
#            E.fd_status = "Error"
#            E.template = 'bkp/stats/main_statistics.html'
#
#        update_diskusage_graph( IMAGENS_DIR + "disk.png")    
#
#        return E.render()
#    
#
@authentication_required
def history_statistics(request):
    return HttpResponseRedirect(utils.reverse('stats_global'))
