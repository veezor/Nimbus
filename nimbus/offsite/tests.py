"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""


import mock
import random
from django.test import TestCase

from nimbus.offsite import queue_service


class QueueReporterTest(TestCase):

    def _make_procedures(self, size=10):
        result = []
        for x in xrange(size):
            procedure = mock.Mock()
            procedure.name = "procedure-{0}".format(x)
            procedure.id = x
            result.append(procedure)
        return result

    def _make_requests(self, size=10):
        result = []
        for x in xrange(size):
            request = mock.Mock()
            request.last_update = random.randint(0, 100000)
            request.created_at = random.randint(0, 100000)
            request.rate = random.randint(0, 10)
            request.volume.filename = "filename-{0}".format(random.randint(0, 1000))
            request.volume.size = random.randint(0, 1000000)
            request.transferred_bytes = random.randint(0, request.volume.size)
            request.procedure = random.choice(self.procedures)
            result.append(request)
            self._generate_expected_data(request)
        return result


    def _generate_expected_data(self, request):
        key = request.procedure.name
        if not key in self.expected_data:
            self.expected_data[key] = {}
            self.expected_data[key]['procedure'] = request.procedure

        data = self.expected_data[key]
        data['total'] = data.get('total', 0) + request.volume.size
        data['done'] = data.get('done', 0) + request.transferred_bytes

        if request.last_update > data.get('last', -1):
            data['last'] = request.last_update
            data['current_file'] = request.volume.filename
            data['speed'] = request.rate

        if request.created_at < data.get('added', 100000):
            data['added'] = request.created_at




    def _make_active_requests(self, size=3):
        active_requests = set()

        while len(active_requests) != size:
            req = random.choice(self.requests)
            if not req in active_requests:
                active_requests.add(req)
        return active_requests


    def _make_queue_manager(self):
        queue_manager = mock.Mock()
        queue_manager.list_queues.return_value = ("min",)
        queue_manager.get_requests_on_queue.return_value = self.requests
        queue_manager.get_active_requests.return_value = self._make_active_requests()
        return queue_manager


    def setUp(self):
        self.expected_data = {}
        self.procedures = self._make_procedures()
        self.requests = self._make_requests()
        self.queue_manager = self._make_queue_manager()
        self.queue_reporter = queue_service.QueueProgressReporter(self.queue_manager)
        self.data = self.queue_reporter.export_data()


    def test_names(self):
        procedures_name = set( p.name for p in self.procedures )
        names = set( d['name'] for d in self.data )
        self.assertTrue( names.issubset(procedures_name) )


    def test_ids(self):
        procedures_id = set( p.id for p in self.procedures )
        ids = set( d['id'] for d in self.data )
        self.assertTrue( ids.issubset(procedures_id) )

    def test_names_ids(self):
        procedures_data = set( (p.name,p.id) for p in self.procedures )
        data = set( (d['name'],d['id']) for d in self.data )
        self.assertTrue( data.issubset(procedures_data) )

    def generic_test_field(field_name):
        def test(self):
            for data in self.data:
                procedure_name = data['name']
                self.assertEquals(data[field_name], self.expected_data[procedure_name][field_name])


        test.__name__ = "test_" + field_name
        return test

    test_total = generic_test_field('total')
    test_speed = generic_test_field('speed')
    test_added = generic_test_field('added')
    test_done = generic_test_field('done')
    test_current_file = generic_test_field('current_file')
    del generic_test_field

