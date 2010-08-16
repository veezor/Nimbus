#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from threading import Thread
from Queue import Queue

class WorkerThread(Thread):

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.setDaemon(False)
        self.pool = Queue()
        self.logger = logging.getLogger(__name__)
        self.logger.info("worker thread initialized")



    def add_job(self, callable, args, kwargs):
        self.pool.put( (callable, args, kwargs ) )
        self.logger.info("Add to (%s,%s,%s) WorkerThrad" % \
                (callable, args, kwargs))


    def run(self):
        while True:
            try:
                self.logger.info("worker thread trying get something")
                callable, args, kwargs = self.pool.get()
                callable(*args, **kwargs)
                self.logger.info("worker thread get and call sucessful")
            except Exception, error:
                self.logger.exception("Erro ao processor callable em workerthread")
