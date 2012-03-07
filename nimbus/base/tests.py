"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import re
import datetime

from django.test import TestCase
from nimbus.base import models, admin

class NotificationModelTest(TestCase):


    def test_unicode(self):
        notification = models.Notification(message="Hello",
                                           link="http://trynimbus.com")
        self.assertEqual(unicode(notification), notification.message)




class ConcreteSingletonBaseModel(models.SingletonBaseModel):
    pass


class SingletonBaseModelTest(TestCase):

    def setUp(self):
        self.singleton = ConcreteSingletonBaseModel()
    
    def test_exists(self):
        self.assertFalse( self.singleton.exists())
        self.singleton.save()
        self.assertTrue( self.singleton.exists())

    def test_id_1(self):
        self.singleton.save()
        self.assertEqual(self.singleton.id, 1)
        other_singleton = ConcreteSingletonBaseModel()
        other_singleton.save()
        self.assertEqual(other_singleton.id, 1)

    def test_get_instance(self):
        self.singleton.save()
        singleton = ConcreteSingletonBaseModel.get_instance()
        self.assertEqual(self.singleton, singleton)

    def test_get_instance_when_not_exist(self):
        # XXX not same id
        singleton = ConcreteSingletonBaseModel.get_instance()
        self.assertEqual(self.singleton, singleton)


class UUIDModelTest(TestCase):

    def setUp(self):
        self.uuid = models.UUID()

    def test_create_uuid(self):
        self.assertEqual(self.uuid.uuid_hex, u'none')
        self.uuid.save()
        self.assertNotEqual(self.uuid.uuid_hex, u'none')

    def test_uuid_hexx(self):
        self.uuid.save()
        uuid_re = re.compile("\w{32}")
        match = uuid_re.match(self.uuid.uuid_hex)
        self.assertNotEqual(match, None)


    def test_created_on(self):
        created_on = self.uuid.created_on
        diff = datetime.datetime.now()  - created_on
        self.assertTrue(diff.seconds < 10)

    def test_violation(self):
        self.uuid.save()
        self.assertRaises(models.UUIDViolation, self.uuid.save)


    def test_unicode(self):
        self.assertEqual( unicode(self.uuid), 
                u"none " + unicode(self.uuid.created_on))
        self.uuid.save()
        self.assertEqual( unicode(self.uuid), 
                self.uuid.uuid_hex + " " + unicode(self.uuid.created_on))



class ConcreteUUIDBaseModel(models.UUIDBaseModel):
    pass

class UUIDBaseModelTest(TestCase):

    def setUp(self):
        self.model = ConcreteUUIDBaseModel()
    
    def test_uuid_fail(self):
        self.assertRaises(models.UUID.DoesNotExist, lambda: self.model.uuid)

    def test_bacula_name(self):
        self.model.save()
        bacula_name = self.model.uuid.uuid_hex + "_concreteuuidbasemodel"
        self.assertEqual(self.model.bacula_name, bacula_name)

    def test_create_uuid(self):
        self.assertRaises(models.UUID.DoesNotExist, lambda: self.model.uuid)
        self.model.save()
        try:
            self.model.uuid
            raised = False
        except models.UUID.DoesNotExist:
            raised = True
        self.assertFalse(raised)


    #TODO Test system_security on security app





class ConcreteUUIDSingletonModel(models.UUIDSingletonModel):
    pass


class UUIDSingletonModelTest(TestCase):

    def setUp(self):
        self.model = ConcreteUUIDSingletonModel()

    def test_uuid(self):
        #XXX DRY
        self.assertRaises(models.UUID.DoesNotExist, lambda: self.model.uuid)
        self.model.save()
        try:
            self.model.uuid
            raised = False
        except models.UUID.DoesNotExist:
            raised = True
        self.assertFalse(raised)


    def test_singleton(self):
        self.model.save()
        self.assertEqual(self.model.id, 1)
        other_model = ConcreteUUIDSingletonModel()
        other_model.save()
        self.assertEqual(other_model.id, 1)



class BaseAdminRegistry(TestCase):

    def test_uuid(self):
        self.assertTrue( models.UUID in admin.admin.site._registry)

    def test_notification(self):
        self.assertTrue( models.Notification in admin.admin.site._registry)
