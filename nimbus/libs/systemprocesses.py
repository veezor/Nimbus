#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import backgroundjobs
from backgroundjobs import MIN_PRIORITY, NORM_PRIORITY, MAX_PRIORITY
from nimbus.shared.middlewares import ThreadPool



def min_priority_job(description, callback, *args, **kwargs):
    job = backgroundjobs.Job(description, MIN_PRIORITY, 
                              callback, *args, **kwargs)
    threadpool = ThreadPool.get_instance()
    if threadpool:
        threadpool.add_job(job)


def norm_priority_job(description, callback, *args, **kwargs):
    job = backgroundjobs.Job(description, NORM_PRIORITY, 
                              callback, *args, **kwargs)
    threadpool = ThreadPool.get_instance()
    if threadpool:
        threadpool.add_job(job)


def max_priority_job(description, callback, *args, **kwargs):
    job = backgroundjobs.Job(description, MAX_PRIORITY, 
                               callback, *args, **kwargs)
    threadpool = ThreadPool.get_instance()
    if threadpool:
        threadpool.add_job(job)



def has_pending_jobs():
    threadpool = ThreadPool.get_instance()
    if threadpool:
        return bool(threadpool.list_jobs_pending())

