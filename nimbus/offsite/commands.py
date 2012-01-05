#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xmlrpclib
from nimbus.libs.commands import command
from nimbus.offsite import models
from nimbus.offsite import managers
from nimbus.offsite import queue_service


@command("--upload-requests")
def create_upload_requests(args):
    u"""Parâmetro: Lista de volumes. Ex: volume1|volume2|volume3
    Solicita o upload de volumes a fila do offsite"""
    try:
        volumes = args.split('|')
        volumes = filter(None, volumes)
        volumes = managers.get_volumes_abspath( volumes )
        manager = managers.RemoteManager()

        for volume in volumes:
            manager.create_upload_request( volume )


        manager.generate_database_dump_upload_request()

        queue_manager = queue_service.get_queue_service_manager()
        requests = manager.get_upload_requests()
        for request in requests:
            try:
                queue_manager.add_request(request.id)
            except xmlrpclib.Fault:
                pass

    except IndexError, error:
        # not args.
        pass


@command("--upload-now")
def upload_volumes():
    u"""Envia os volumes pendentes do offsite imediatamente"""
    manager = managers.RemoteManager()
    manager.process_pending_upload_requests()


@command("--delete-volumes")
def delete_volumes():
    u"""Deleta os volumes pendentes do offsite imediatamente"""
    manager = managers.RemoteManager()
    manager.process_pending_delete_requests()


@command("--start-queue-service")
def start_queue_service():
    u"""Inicia o serviço da fila de offsite"""
    queue_service.start_queue_manager_service()


@command("--offsite-simple-config")
def offsite_simple_config(username, password):
    u"""Configuração simples do offsite.
    Use --offsite-simple-config username password"""
    offsite = models.Offsite.get_instance()
    offsite.username = username
    offsite.password = password
    offsite.active = True
    offsite.clean()
    offsite.save()
