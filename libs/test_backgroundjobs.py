#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import unittest
import datetime
import backgroundjobs


class TestSynchronized(unittest.TestCase):
    #TODO
    pass

class TestJob(unittest.TestCase):

    def test_new_id(self):
        self.assertEqual(backgroundjobs.NullJob.id, 1)

        backgroundjobs.Job.jobid = 1 #XXX

        job1 = backgroundjobs.Job("test 1",
                                  backgroundjobs.MIN_PRIORITY,
                                  lambda : "Hello World")
        self.assertEqual(job1.id, 2)

        job2 = backgroundjobs.Job("test 2",
                                  backgroundjobs.MIN_PRIORITY,
                                  lambda : "Hello World")
        self.assertEqual(job2.id, 3)



    def test_new(self):
        description = "test 1"
        callback = lambda : "Hello World"
        job1 = backgroundjobs.Job(description,
                                  backgroundjobs.MIN_PRIORITY,
                                  callback)
        self.assertEqual(job1.description, description)
        self.assertEqual(job1.callback, callback)
        self.assertEqual(job1.priority, backgroundjobs.MIN_PRIORITY)
        self.assertEqual(job1.args, tuple())
        self.assertEqual(job1.kwargs, {})
        self.assertEqual(job1.pending, True)

        description = "test 2"
        callback = lambda : "Hello World 2"
        job2 = backgroundjobs.Job(description,
                                  backgroundjobs.MAX_PRIORITY,
                                  callback,
                                  1,2,3,4,5,
                                  kwargs1=1,kwargs2=2)
        self.assertEqual(job2.priority, backgroundjobs.MAX_PRIORITY)
        self.assertEqual(job2.kwargs, {"kwargs1":1,"kwargs2":2})
        self.assertEqual(job2.args, (1,2,3,4,5))


    def test_call(self):
        description = "test 1"
        callback = lambda : "Hello World"
        job1 = backgroundjobs.Job(description,
                                  backgroundjobs.MIN_PRIORITY,
                                  callback)
        rvalue = job1.invoke()
        self.assertEqual(rvalue, "Hello World")
        self.assertEqual(job1.pending, False)


    def test_max_priority_job(self):
        job = backgroundjobs.max_priority_job("description",
                                              lambda : None)
        self.assertEqual(job.priority, backgroundjobs.MAX_PRIORITY)


    def test_norm_priority_job(self):
        job = backgroundjobs.norm_priority_job("description",
                                              lambda : None)
        self.assertEqual(job.priority, backgroundjobs.NORM_PRIORITY)





if __name__ == "__main__":
    unittest.main()
