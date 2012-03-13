#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import time
import unittest
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



def make_job(priority=backgroundjobs.MIN_PRIORITY,
             callback = lambda : "Hello World"):
    description = "test 1"
    job1 = backgroundjobs.Job(description,
                              priority,
                              callback)
    return job1




class WorkerThreadTest(unittest.TestCase):




    def setUp(self):
        self.wt = backgroundjobs.WorkerThread()
        self.job = make_job()


    def test_add(self):
        self.wt.add_job(self.job)
        self.assertTrue( self.job in self.wt.get_jobs() )
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 1 )
        self.assertEqual( self.wt.get_num_jobs(), 1 )


    def test_get_num_jobs(self):
        self.assertEqual( self.wt.get_num_jobs(), 0 )
        self.wt.add_job(self.job)
        self.assertEqual( self.wt.get_num_jobs(), 1 )


    def test_heavyweight(self):
        job2 = make_job(backgroundjobs.MAX_PRIORITY)
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 0 )
        self.wt.add_job(self.job)
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 1 )
        self.wt.add_job(job2)
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 1 )



    def test_get_jobs(self):
        self.assertEqual([], self.wt.get_jobs())
        self.wt.add_job(self.job)
        self.assertEqual([self.job], self.wt.get_jobs())


    def test_remove_jobs(self):
        self.wt.add_job(self.job)
        self.assertEqual( self.wt.get_num_jobs(), 1 )
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 1 )
        self.wt.remove_job(self.job)
        self.assertEqual( self.wt.get_num_jobs(), 0 )
        self.assertEqual( self.wt.get_num_heavyweight_jobs(), 0 )


    def test_run(self):
        self.wt.add_job(self.job)
        self.assertEqual(self.job.pending, True)
        self.wt.start()
        time.sleep(2.0)
        self.assertFalse(self.wt.has_stopped)
        self.wt.stop()
        self.assertEqual(self.job.pending, False)
        self.assertTrue(self.wt.has_stopped)



class ThreadPoolTest(unittest.TestCase):

    def setUp(self):
        self.job = make_job()
        self.thread_pool = backgroundjobs.ThreadPool()


    def test_has_job_pending(self):
        self.assertFalse( self.thread_pool.has_job_pending(self.job.id) )
        self.thread_pool.add_job(self.job)
        self.assertTrue( self.thread_pool.has_job_pending(self.job.id) )
        self.thread_pool.stop()

    def test_list_jobs_pending(self):
        self.assertEqual( self.thread_pool.list_jobs_pending(), [] )
        self.thread_pool.add_job(self.job)
        self.assertEqual( self.thread_pool.list_jobs_pending(), [self.job] )
        self.thread_pool.stop()


    def test_stop(self):
        self.thread_pool.add_job(self.job)
        self.thread_pool.stop() # if stop fails tests blocks forever


    def test_run(self):
        self.assertEqual(self.job.pending, True)
        self.thread_pool.add_job(self.job)
        time.sleep(2.0)
        self.thread_pool.stop()
        self.assertEqual(self.job.pending, False)


    def test_run_many_jobs(self):
        def callback():
            time.sleep(1.0)
        jobs = [ make_job(callback=callback) for x in xrange(6) ] # 6 > 5. default value of max_workers
        for job in jobs:
            self.thread_pool.add_job(job)
        time.sleep(6.0)
        self.thread_pool.stop()
        self.assertEqual(len(self.thread_pool.workers), 5)
        for job in jobs:
            self.assertEqual(job.pending, False)

    def test_run_many_jobs_MAX(self):
        jobs = [ make_job(backgroundjobs.MAX_PRIORITY) for x in xrange(6) ] 
        # 6 > 5. default value of max_workers
        for job in jobs:
            self.thread_pool.add_job(job)
        time.sleep(2.0)
        self.thread_pool.stop()
        for job in jobs:
            self.assertEqual(job.pending, False)
        self.assertEqual(len(self.thread_pool.workers), 1)




if __name__ == "__main__":
    unittest.main()