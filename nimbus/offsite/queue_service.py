#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import weakref
import logging
import xmlrpclib
import SimpleXMLRPCServer
import Queue as PyQueue
from multiprocessing import Process
from threading import Thread, RLock


from django.conf import settings
from django.db.models import Max

from nimbus.offsite.models import (Offsite,
                                   RemoteUploadRequest)
from nimbus.offsite.managers import RemoteManager


class QueueServiceManager(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_priority_queue_manager = PriorityQueueManager("Max Priority Queue", self)
        self.middle_priority_queue_manager = PriorityQueueManager("Middle Priority Queue", self)
        self.min_priority_queue_manager = PriorityQueueManager("Min Priority Queue", self)

        self.lock = RLock()
        self.concurrent_workers = 0
        self.requests = {}
        self.request_queue = {} #DEBUG

        self._load_database_requests()

        self.max_priority_queue_manager.start()
        self.middle_priority_queue_manager.start()
        self.min_priority_queue_manager.start()


    
    #DEBUG
    def _add_request_to_queue(self, request, queue):
        self.request_queue[ request.id ] = queue.getName()


    def get_requests_on_queue(self, queue_name):
        result = []

        for (request, q_name) in self.request_queue.items():
            if q_name == queue_name:
                try:
                    req = self._get_request(request)
                    result.append( req )
                except RemoteUploadRequest.DoesNotExist:
                    pass

        return result


    def get_volumes_on_queue(self, queue_name):
        return [ req.volume.filename\
                for req in self.get_requests_on_queue(queue_name) ]


    def get_active_requests(self):
        result = []

        def add(queue):
            if not queue.current_request is None:
                result.append( queue.current_request )

        add(self.max_priority_queue_manager)
        add(self.min_priority_queue_manager )
        add(self.middle_priority_queue_manager )
        return result


    def list_queues(self):
        return ["Max Priority Queue", "Min Priority Queue", "Middle Priority Queue"]
    #END DEBUG


    @property
    def ratelimit(self):
        self.logger.info('QueueServiceManager.ratelimit')
        offsite = Offsite.get_instance()
        return offsite.rate_limit

    def increase_concurrent_workers(self):
        with self.lock:
            self.logger.info('QueueServiceManager.increase_concurrent_workers')
            self.concurrent_workers += 1


    def decrease_concurrent_workers(self):
        with self.lock:
            self.logger.info('QueueServiceManager.decrease_concurrent_workers')
            self.concurrent_workers -= 1


    def get_concurrent_workers(self):
        with self.lock:
            self.logger.info('QueueServiceManager.get_concurrent_workers')
            return self.concurrent_workers


    def get_worker_ratelimit(self):
        if self.get_concurrent_workers():
            self.logger.info('QueueServiceManager.get_worker_ratelimit')
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
            self.logger.info('QueueServiceManager._get_queue_manager = max. request = %s' % request)
            return self.max_priority_queue_manager
        elif ratio <= 0.6:
            self.logger.info('QueueServiceManager._get_queue_manager = middle. request = %s' % request)
            return self.middle_priority_queue_manager
        else:
            self.logger.info('QueueServiceManager._get_queue_manager = min. request = %s' % request)
            return self.min_priority_queue_manager


    def _load_database_requests(self):
        self.logger.info('QueueServiceManager.load_database')
        for request in RemoteUploadRequest.objects.all():
            self.add_request(request.id)


    def _get_request(self, request_id):
        return RemoteUploadRequest.objects.get(id=request_id)


    def add_request(self, request_id):

        if request_id in self.requests:
            return

        self.logger.info('adicionando request id=%d' % request_id)
        request = self._get_request(request_id)
        queue_manager = self._get_queue_manager(request)

        with self.lock:
            self.requests[request_id] = queue_manager

        self._add_request_to_queue(request, queue_manager)
        queue_manager.add_request(request)
        self.logger.info('request id=%d adicionado com sucesso' % request_id)


    def cancel_request(self, request_id):
        self.logger.info('cancelando request')
        request = self._get_request(request_id)

        queue_manager = self.requests[request_id]
        queue_manager.cancel_request(request)

        del self.requests[request_id]
        request.delete()
        self.logger.info('request cancelado')


    def set_request_as_done(self, request_id):
        with self.lock:
            self.logger.info('set_request_as_done')
            del self.requests[request_id]
            del self.request_queue[request_id]


    def run_delete_agent(self):
        agent = DeleteAgent()
        agent.start()



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

    def list_queues(self):
        return self.service_manager.list_queues()

    def get_volumes_on_queue(self, queue_name):
        return self.service_manager.get_volumes_on_queue(queue_name)

    def get_progress_data(self):
        return QueueProgressReporter(self.service_manager).export_data()

    def run_delete_agent(self):
        self.service_manager.run_delete_agent()
        return True

    def increase_concurrent_workers(self):
        self.service_manager.increase_concurrent_workers()
        return True

    def check_service(self):
        return True




class PriorityQueueManager(Thread):

    def __init__(self, name, service_manager):
        super(PriorityQueueManager, self).__init__()
        self.setName(name)
        self.logger = logging.getLogger(__name__)
        self.service_manager = weakref.ref(service_manager)
        self.queue = Queue()
        self.current_worker = None
        self.current_request = None
        self.running = False


    def run(self):
        self.running = True
        while self.running:
            self.logger.info('PQM tick ' + self.getName() )
            request = self.queue.get()
            self.logger.info('PQM get request = ' + str(request)  + ' ' + self.getName() )
            service_manager = self.service_manager()
            service_manager.increase_concurrent_workers()
            self._start_worker(request)
            service_manager.decrease_concurrent_workers()


    def stop(self):
        self.logger.info('PQM stop '  + self.getName() )
        self.running = False
        self._stop_current_worker()


    def _stop_current_worker(self, cancel_current_request=False):
        self.logger.info('PQM set current worker')
        if self.current_worker:
            self.current_worker.terminate()
            if not cancel_current_request:
                self.add_request(self.current_worker.request)


    def add_request(self, request):
        self.logger.info('PQM adicionando request ' + self.getName())
        self.queue.put(request)
        self.logger.info('PQM request adicionado' + self.getName())


    def cancel_request(self, request):
        self.logger.info('PQM cancel request')
        if request == self.current_request:
            self._stop_current_worker(cancel_current_request=True)
        else:
            self.queue.remove(request)


    def _start_worker(self, request):
        self.logger.info('PQM start worker ' + self.getName())
        worker = Worker(request.id)
        self.current_worker = worker
        self.current_request = request

        worker.start()
        self.logger.info('PQM worker started ' + self.getName() + " pid=" + str(worker.pid))
        worker.join()
        self.logger.info('PQM worker end with ' + str(worker.exitcode) + " " + self.getName()  + " pid=" + str(worker.pid))

        if worker.exitcode != 0:
            # -15[kill] == cancel
            self.logger.info('PQM re-add request ' + self.getName())
            self.logger.info('PQM re-add request ' + str(request))
            self.add_request(request)

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

    def __init__(self, request_id):
        super(Worker, self).__init__()
        self.request_id = request_id


    def run(self):
        self.logger = logging.getLogger(__name__)

        manager = RemoteManager()

        try:
            self.request = RemoteUploadRequest.objects.get(id=self.request_id)
            self.logger.info(str(self.pid) + ' starting process request' + str(self.request))
            manager.upload_volume(self.request)
            self.logger.info(str(self.pid) + ' request %s uploaded with sucess' % str(self.request))
            set_request_as_done(self.request_id)
            self.logger.info(str(self.pid) + ' request %s marked as sucessful' % str(self.request))
        except OSError, error:
            self.logger.exception(str(self.pid) + ' file not found. Probably procedure delete (%s)' % self.request_id)
            set_request_as_done(self.request_id)
            self.request.delete()
        except IOError, error:
            self.logger.exception(str(self.pid) + ' request %s upload error' % self.request_id)
            sys.exit(2)
        except RemoteUploadRequest.DoesNotExist, error:
            self.logger.exception(str(self.pid) + ' request %s upload error. Request does not exist' % self.request_id)
            try:
                set_request_as_done(self.request_id)
            except xmlrpclib.Fault:
                pass
        except Exception, error:
            self.logger.exception(str(self.pid) + ' request %s upload uncatched error' % self.request_id)
            sys.exit(2)




def start_queue_manager_service():
    service = QueueServiceManager()
    facade = QueueServiceManagerFacade(service)
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((settings.QUEUE_SERVICE_MANAGER_ADDRESS,
                                                    settings.QUEUE_SERVICE_MANAGER_PORT))
    server.register_instance(facade)
    server.serve_forever()


def get_queue_service_manager():
    proxy = xmlrpclib.ServerProxy(settings.QUEUE_SERVICE_MANAGER_URL)
    proxy.check_service()
    return proxy



def get_worker_ratelimit():
    service_manager = get_queue_service_manager()
    ratelimit = service_manager.get_worker_ratelimit()
    if ratelimit < 0:
        return -1

    return ratelimit



def set_request_as_done(request_id):
    service_manager = get_queue_service_manager()
    service_manager.set_request_as_done(request_id)


def get_queue_progress_data():
    service_manager = get_queue_service_manager()
    return service_manager.get_progress_data()


class DeleteAgent(Thread):

    def run(self):
        from nimbus.offsite.managers import RemoteManager
        remote_manager = RemoteManager()
        remote_manager.process_pending_delete_requests()




class QueueProgressReporter(object):

    def __init__(self, queue_manager):
        self.queue_manager = queue_manager

    def _get_requests_on_queues(self):
        result = []
        for queue in self.queue_manager.list_queues():
            result.extend( self.queue_manager.get_requests_on_queue(queue) )
        return result


    def _get_recent_request_from_job(self, requests):
        key_func = lambda req: req.last_update
        request = sorted(requests, key=key_func, reverse=True)[0]
        return request


    def _get_recent_volume_from_job(self, requests ):
        request = self._get_recent_request_from_job(requests)
        return request.volume.filename

    def _get_start_time_from_job(self, requests ):
        key_func = lambda req: req.created_at
        request = sorted(requests, key=key_func)[0]
        return request.created_at.strftime("%H:%M:%S de %d/%m/%Y")


    def _get_rate_from_job(self, requests):
        request = self._get_recent_request_from_job(requests)
        return request.rate

    def _get_total_size_from_job(self, requests):
        return sum( req.volume.size for req in requests )

    def _get_transferred_bytes_from_job(self, requests):
        return sum( req.transferred_bytes for req in requests )

    def _group_by_job(self, requests):
        jobs = {}
        for req in requests:
            job = req.job
            if not job in jobs:
                jobs[job] = []

            jobs[job].append(req)

        return jobs

    def _get_active_jobs(self):
        requests = self.queue_manager.get_active_requests()
        return [ req.job for req in requests ]


    def export_data(self):
        result = []
        requests = self._get_requests_on_queues()
        requests_by_job = self._group_by_job(requests)
        active_jobs = self._get_active_jobs()
        for job, p_requests in requests_by_job.items():
            data = {}
            data['name'] = job.procedure.name
            data['id'] = job.jobid
            data['total'] = self._get_total_size_from_job(p_requests)
            data['done'] = self._get_transferred_bytes_from_job(p_requests)

            if job in active_jobs:
                data['speed'] = self._get_rate_from_job(p_requests)
            else:
                data['speed'] = 0

            data['current_file'] = self._get_recent_volume_from_job(p_requests)
            data['added'] = self._get_start_time_from_job(p_requests)
            result.append(data)
        key_func = lambda item: item['added']
        return sorted(result, key=key_func)


