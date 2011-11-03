#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.libs.commands import command
from nimbus.libs import offsite
from nimbus.offsite import queue_service


@command("--upload-requests")
def create_upload_requests(args):
    try:
        volumes = args.split('|')
        volumes = filter(None, volumes)
        volumes = offsite.get_volumes_abspath( volumes )
        manager = offsite.RemoteManager()

        for volume in volumes:
            manager.create_upload_request( volume )

        manager.generate_database_dump_upload_request()
        manager.process_pending_upload_requests()
    except IndexError, error:
        # not args.
        pass


@command("--upload-now")
def upload_volumes():
    manager = offsite.RemoteManager()
    manager.process_pending_upload_requests()


@command("--delete-volumes")
def delete_volumes():
    manager = offsite.RemoteManager()
    manager.process_pending_delete_requests()


@command("--start-queue-service")
def start_queue_service():
    queue_service.start_queue_manager_service()


