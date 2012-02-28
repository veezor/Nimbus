#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
import unittest
import backgroundjobs

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from nimbus.libs import systemprocesses
from nimbus.shared.middlewares import LogSetup,ThreadPool

LogSetup()
ThreadPool()

class SystemProcessTest(unittest.TestCase):


    def setUp(self):
        ThreadPool.instance = backgroundjobs.ThreadPool()
        self.thread_pool = ThreadPool.instance

        def callback():
            time.sleep(1)

        self.callback = callback


    def tearDown(self):
        time.sleep(3)
        self.thread_pool.stop()


    def test_pending_jobs(self):
        job = backgroundjobs.min_priority_job("test", self.callback)
        self.assertFalse( systemprocesses.has_pending_jobs() )
        self.thread_pool.add_job(job)
        self.assertTrue( systemprocesses.has_pending_jobs() )


    def test_min_priority_jobs(self):
        systemprocesses.min_priority_job("test", self.callback)
        self.assertEqual( len(self.thread_pool.list_jobs_pending()), 1 )
        job = self.thread_pool.list_jobs_pending()[0]
        self.assertEqual( job.callback, self.callback )
        self.assertEqual( job.priority, backgroundjobs.MIN_PRIORITY )



    def test_norm_priority_jobs(self):
        systemprocesses.norm_priority_job("test", self.callback)
        self.assertEqual( len(self.thread_pool.list_jobs_pending()), 1 )
        job = self.thread_pool.list_jobs_pending()[0]
        self.assertEqual( job.callback, self.callback )
        self.assertEqual( job.priority, backgroundjobs.NORM_PRIORITY)


    def test_max_priority_jobs(self):
        systemprocesses.max_priority_job("test", self.callback)
        self.assertEqual( len(self.thread_pool.list_jobs_pending()), 1 )
        job = self.thread_pool.list_jobs_pending()[0]
        self.assertEqual( job.callback, self.callback )
        self.assertEqual( job.priority, backgroundjobs.MAX_PRIORITY)




if __name__ == "__main__":
    unittest.main()

