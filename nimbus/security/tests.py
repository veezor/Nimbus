#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
from django.test import TestCase


from nimbus.base.models import UUIDSingletonModel
from nimbus.security import models, exceptions, lib, middlewares

from django.contrib.contenttypes.models import ContentType

# for tests only

class ConcreteUUIDSingletonModel(UUIDSingletonModel):
    pass

#

class SecurityTest(TestCase):

    
    def setUp(self):
        self.model = ConcreteUUIDSingletonModel.objects.create()

    def test_register_object(self):
        self.assertEqual(models.AdministrativeModel.objects.count(), 0)
        models.register_object(self.model)
        self.assertEqual(models.AdministrativeModel.objects.count(), 1)

    def test_register_object_from_id(self):
        self.assertEqual(models.AdministrativeModel.objects.count(), 0)
        content_type = ContentType.objects.get(app_label="security", 
                                               model="ConcreteUUIDSingletonModel".lower())
        models.register_object_from_id(content_type, 
                                       object_id=1)
        self.assertEqual(models.AdministrativeModel.objects.count(), 1)


    def test_register_object_from_model_name(self):
        self.assertEqual(models.AdministrativeModel.objects.count(), 0)
        models.register_object_from_model_name("security",
                                               "ConcreteUUIDSingletonModel".lower(),
                                               object_id=1)
        self.assertEqual(models.AdministrativeModel.objects.count(), 1)


    def test_register_objects_from_tuple(self):
        self.assertEqual(models.AdministrativeModel.objects.count(), 0)
        data_tuple = ( ("security", "ConcreteUUIDSingletonModel".lower(),1) , )
        models.register_objects_from_tuple( *data_tuple )
        self.assertEqual(models.AdministrativeModel.objects.count(), 1)


    def test_register_administrative_nimbus_models(self):
        with mock.patch("nimbus.security.models.register_objects_from_tuple")\
                as mock_register:
            models.register_administrative_nimbus_models()
            mock_register.assert_called_with(("computers", "computer", 1),
                                            ("computers", "cryptoinfo", 1),
                                            ("filesets", "fileset", 1),
                                            ("filesets", "filepath", 1),
                                            ("filesets", "filepath", 2),
                                            ("filesets", "filepath", 3),
                                            ("filesets", "filepath", 4),
                                            ("schedules", "schedule", 1),
                                            ("schedules", "run", 1),
                                            ("schedules", "run", 2),
                                            ("schedules", "backupkind", 1),
                                            ("schedules", "backupkind", 2),
                                            ("schedules", "backupkind", 3),
                                            ("schedules", "backupkind", 4),
                                            ("schedules", "backuplevel", 1),
                                            ("schedules", "backuplevel", 2),
                                            ("procedures", "procedure", 1),
                                            ("storages", "storage", 1),
                                            ("storages", "device", 1))


    def test_check_permission(self):
        try:
            lib.check_permission(self.model)
            raised=False
        except exceptions.AdministrativeModelError:
            raised=True
        self.assertFalse(raised)
        models.register_object(self.model)
        self.assertRaises(exceptions.AdministrativeModelError,
                          lib.check_permission, self.model)


    def test_save(self):
        try:
            self.model.save()
            raised=False
        except exceptions.AdministrativeModelError:
            raised=True

        self.assertFalse(raised)
        models.register_object(self.model)
        self.assertRaises(exceptions.AdministrativeModelError,
                          lambda : self.model.save())



    def test_middleware(self):
        with mock.patch("nimbus.security.middlewares.messages") as messages:
            with mock.patch("nimbus.security.middlewares.redirect") as redirect:
                middleware = middlewares.AdministrativeModelChangeCatcher()
                request = mock.Mock()
                request.META = {"PATH_INFO" : "test"}

                result = middleware.process_exception(request, None)
                self.assertEqual(result, None)
                self.assertFalse(redirect.called)
                self.assertFalse(messages.error.called)
                
                result = middleware.process_exception(request,
                            exceptions.AdministrativeModelError())
                redirect.assert_called_with(request.META["PATH_INFO"])
                messages.error.assert_called_with(request, 
                                                  u"Impossível alterar esse elemento.")

