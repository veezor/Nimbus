#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import socket
import weakref
import xmlrpclib
import subprocess
import SimpleXMLRPCServer
import Queue as PyQueue
from multiprocessing import Process
from threading import Thread, RLock


from django.conf import settings
from django.db.models import Max

from nimbus.offsite.models import (Offsite,
                                   RemoteUploadRequest)


class QueueServiceManager(object):

    def __init__(self):
        self.max_priority_queue_manager = PriorityQueueManager(self)
        self.middle_priority_queue_manager = PriorityQueueManager(self)
        self.min_priority_queue_manager = PriorityQueueManager(self)

        self.lock = RLock()
        self.concurrent_workers = 0
        self.requests = {}

        self._load_database_requests()

        self.max_priority_queue_manager.start()
        self.middle_priority_queue_manager.start()
        self.min_priority_queue_manager.start()




    @property
    def ratelimit(self):
        offsite = Offsite.get_instance()
        return offsite.rate_limit

    def increase_concurrent_workers(self):
        with self.lock:
            self.concurrent_workers += 1


    def decrease_concurrent_workers(self):
        with self.lock:
            self.concurrent_workers -= 1


    def get_concurrent_workers(self):
        with self.lock:
            return self.concurrent_workers


    def get_worker_ratelimit(self):
        if self.get_concurrent_workers():
            return self.ratelimit / float(self.get_concurrent_workers())
        else:
            return 0


    def _get_max_volume_size(self):
        data = RemoteUploadRequest.objects.aggregate(max=Max('volume__size'))
        return data['max'] or 0


    def _get_queue_manager(self, request):
        volume_size = request.volume.size


        if not self._get_max_volume_size():
            return self.max_priority_queue_manager

        ratio = volume_size / float(self._get_max_volume_size())

        if ratio <= 0.2:
            return self.max_priority_queue_manager
        elif ratio <= 0.6:
            return self.middle_priority_queue_manager
        else:
            return self.min_priority_queue_manager


    def _load_database_requests(self):
        for request in RemoteUploadRequest.objects.all():
            self.add_request(request.id)


    def _get_request(self, request_id):
        return RemoteUploadRequest.objects.get(id=request_id)


    def add_request(self, request_id):
        request = self._get_request(request_id)
        queue_manager = self._get_queue_manager(request)

        with self.lock:

            if request_id in self.requests:
                raise ValueError('request already exists')

            self.requests[request_id] = queue_manager

        queue_manager.add_request(request)


    def cancel_request(self, request_id):
        request = self._get_request(request_id)

        queue_manager = self.requests[request_id]
        queue_manager.cancel_request(request)

        del self.requests[request_id]
        request.delete()


    def set_request_as_done(self, request_id):
        with self.lock:
            del self.requests[request_id]




class QueueServiceManagerFacade(object):

    def __init__(self, service_manager):
        self.service_manager = service_manager

    def add_request(self, request_id):
        self.service_manager.add_request(request_id)
        return True

    def cancel_request(self, request_id):
        self.service_manager.cancel_request(request_id)
        return True

    def get_worker_ratelimit(self):
        return self.service_manager.get_worker_ratelimit()

    def set_request_as_done(self, request_id):
        self.service_manager.set_request_as_done(request_id)
        return True

    def check_service(self):
        return True




class PriorityQueueManager(Thread):

    def __init__(self, service_manager):
        super(PriorityQueueManager, self).__init__()
        self.service_manager = weakref.ref(service_manager)
        self.queue = Queue()
        self.current_worker = None
        self.current_request = None
        self.running = False


    def run(self):

        self.running = True
        while self.running:
            request = self.queue.get()
            service_manager = self.service_manager()
            service_manager.increase_concurrent_workers()
            self._start_worker(request)
            service_manager.decrease_concurrent_workers()


    def stop(self):
        self.running = False
        self._stop_current_worker()


    def _stop_current_worker(self, cancel_current_request=False):
        if self.current_worker:
            self.current_worker.terminate()
            if not cancel_current_request:
                self.add_request(self.current_worker.request)


    def add_request(self, request):
        self.queue.put(request)


    def cancel_request(self, request):
        if request == self.current_request:
            self._stop_current_worker(cancel_current_request=True)
        else:
            self.queue.remove(request)


    def _start_worker(self, request):
        worker = Worker(request)
        self.current_worker = worker
        self.current_request = request

        worker.start()
        worker.join()

        if worker.exitcode == 2:
            # -15[kill] == cancel
            self.add_request(worker.request)

        self.current_worker = None
        self.current_request = None




class Queue(PyQueue.Queue):

    def remove(self, item, block=True, timeout=None):
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise PyQueue.Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = PyQueue._time() + timeout
                while not self._qsize():
                    remaining = endtime - PyQueue._time()
                    if remaining <= 0.0:
                        raise PyQueue.Empty
                    self.not_empty.wait(remaining)
            item = self._remove(item)
            self.not_full.notify()
        finally:
            self.not_empty.release()


    def _remove(self, item):
        self.queue.remove(item)




class Worker(Process):

    MAX_RETRY = 3

    def __init__(self, request):
        super(Worker, self).__init__()
        self.request = request


    def run(self):
        from nimbus.libs.offsite import process_request
        self.s3 = Offsite.get_s3_interface()
        try:
            request_id = self.request.id
            process_request(self.request, self._upload_file,
                            get_worker_ratelimit(), self.MAX_RETRY)
            set_request_as_done(request_id)
        except IOError, error:
            sys.exit(2)


    def _upload_file(self, filename, dest, callback=None, userdata=None):
        self.s3.multipart_status_callbacks.add_callback( userdata.increment_part )
        self.s3.upload_file(filename, dest, part=userdata.part, callback=callback)
        self.s3.multipart_status_callbacks.remove_callback( userdata.increment_part )



def start_queue_manager_service():
    service = QueueServiceManager()
    facade = QueueServiceManagerFacade(service)
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((settings.QUEUE_SERVICE_MANAGER_ADDRESS,
                                                    settings.QUEUE_SERVICE_MANAGER_PORT))
    server.register_instance(facade)
    server.serve_forever()


def _get_queue_service_manager():
    proxy = xmlrpclib.ServerProxy(settings.QUEUE_SERVICE_MANAGER_URL)
    proxy.check_service()
    return proxy



def get_queue_service_manager():
    try:
        return _get_queue_service_manager()
    except socket.error:
        service = subprocess.Popen(settings.QUEUE_SERVICE_MANAGER_COMMAND)
        time.sleep(settings.QUEUE_MANAGER_START_SLEEP_TIME)
        return _get_queue_service_manager()




def get_worker_ratelimit():
    service_manager = get_queue_service_manager()
    ratelimit = service_manager.get_worker_ratelimit()
    if ratelimit < 0:
        return -1

    return ratelimit



def set_request_as_done(request_id):
    service_manager = get_queue_service_manager()
    service_manager.set_request_as_done(request_id)
