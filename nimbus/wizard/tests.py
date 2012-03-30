#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import sys
import mock
from django.test import TestCase

from nimbus.wizard import models, admin, middleware


class WizardTest(TestCase):

    def test_admin(self):
        self.assertTrue( models.Wizard in admin.admin.site._registry)


    def test_unicode(self):
        wizard = models.Wizard(completed=False)
        self.assertEqual( unicode(wizard), u"Wizard(completed=0)")

        wizard = models.Wizard(completed=True)
        self.assertEqual( unicode(wizard), u"Wizard(completed=1)")


    def test_finish(self):
        with mock.patch("nimbus.wizard.models.bacula") as bacula:
            wizard = models.Wizard()
            self.assertEqual(wizard.id, None)
            wizard.finish()
            self.assertNotEqual(wizard.id, None)
            self.assertTrue( isinstance(wizard.id, int))
            bacula.unlock_bacula_and_start.assert_called_with()



class WizardManagerTest(TestCase):

    def setUp(self):
        self.patch = mock.patch("nimbus.wizard.models.wizard_manager",
                                new_callable=models.WizardManager)
        self.wizard_manager = self.patch.start()


    def test_simple_decorator(self):

        @models.add_step()
        def step(request):
            pass

        self.assertEqual( ["step"], self.wizard_manager.get_steps())


    def test_decorator_name(self):

        @models.add_step(name="test-step-name")
        def other_step(request):
            pass

        self.assertEqual( ["test-step-name"], self.wizard_manager.get_steps())



    def test_decorator_position(self):
        @models.add_step(name="test_step", position=2)
        def new_step(request):
            pass

        self.assertEqual( [new_step],
                          self.wizard_manager.at_begin_steps.values()  )
        self.assertEqual( ["test_step"],
                         self.wizard_manager.at_begin_steps.keys()  )

        self.assertEqual( self.wizard_manager.at_begin_positions[new_step], 2  )
        self.assertEqual( self.wizard_manager.at_begin_reversed_positions[2],
                         "test_step"  )


    def test_get_step(self):

        @models.add_step()
        def step(request):
            pass

        self.assertEqual(step, self.wizard_manager.get_step('step'))


    def test_add_step_simple(self):


        def step(request):
            pass

        self.wizard_manager.add_step(step)
        self.assertEqual( ["step"], self.wizard_manager.get_steps())


    def test_add_step_name(self):

        def other_step(request):
            pass

        self.wizard_manager.add_step(other_step, name="test-step-name")

        self.assertEqual( ["test-step-name"], self.wizard_manager.get_steps())



    def test_add_step_position(self):


        def new_step(request):
            pass


        self.wizard_manager.add_step(new_step, name="test_step", position=2)

        self.assertEqual( [new_step],
                          self.wizard_manager.at_begin_steps.values()  )
        self.assertEqual( ["test_step"],
                         self.wizard_manager.at_begin_steps.keys()  )

        self.assertEqual( self.wizard_manager.at_begin_positions[new_step], 2  )
        self.assertEqual( self.wizard_manager.at_begin_reversed_positions[2],
                         "test_step"  )



    def test_add_step_at_begin(self):

        def step(request):
            pass

        self.wizard_manager.add_step(step, position=1)
        self.assertEqual(["step"],
                         self.wizard_manager.get_steps())


    def test_add_step_at_end(self):

        def step(request):
            pass

        self.wizard_manager.add_step(step, position=-1)
        self.assertEqual(["step"],
                         self.wizard_manager.get_steps())


    def test_add_without_position(self):

        def step(request):
            pass

        self.wizard_manager.add_step(step)
        self.assertEqual(["step"],
                         self.wizard_manager.get_steps())



    def test_conflict_position(self):

        def step(request):
            pass

        self.wizard_manager.add_step(step, position=1)

        self.assertEqual(["step"],
                         self.wizard_manager.get_steps())

        def new_step(request):
            pass

        self.assertRaises( models.WizardStepError,
            self.wizard_manager.add_step, new_step, position=1)


    def test_conflict_name(self):

        def step(request):
            pass

        self.wizard_manager.add_step(step, position=1)

        self.assertEqual(["step"],
                         self.wizard_manager.get_steps())

        def new_step(request):
            pass

        self.assertRaises( models.WizardStepError,
            self.wizard_manager.add_step, new_step, name="step")



    def test_add_step(self):

        def step1(request):
            pass

        def step2(request):
            pass

        def step3(request):
            pass

        self.wizard_manager.add_step(step1, position=1)
        self.wizard_manager.add_step(step2)
        self.wizard_manager.add_step(step3, position=-11)

        self.assertEqual( ["step1", "step2", "step3"], 
                          self.wizard_manager.get_steps())


    def test_add_step_ordering(self):

        def step1(request):
            pass

        def step2(request):
            pass


        self.wizard_manager.add_step(step1, position=2)
        self.wizard_manager.add_step(step2, position=1)

        self.assertEqual( ["step2", "step1"], 
                          self.wizard_manager.get_steps())



    def test_next_step(self):

        def step1(request):
            pass

        def step2(request):
            pass

        def step3(request):
            pass

        self.wizard_manager.add_step(step1, position=1)
        self.wizard_manager.add_step(step2, position=2)
        self.wizard_manager.add_step(step3, position=3)

        self.assertEqual( ("step2", step2), 
                          self.wizard_manager.get_next_step(current="step1"))

        self.assertEqual( ("step3", step3), 
                          self.wizard_manager.get_next_step(current="step2"))
        self.assertRaises( models.WizardStepError,
                           self.wizard_manager.get_next_step, current="step3")
                            
 
    def test_previous_step(self):

        def step1(request):
            pass

        def step2(request):
            pass

        def step3(request):
            pass

        self.wizard_manager.add_step(step1, position=1)
        self.wizard_manager.add_step(step2, position=2)
        self.wizard_manager.add_step(step3, position=3)

        
        self.assertRaises( models.WizardStepError,
                           self.wizard_manager.get_previous_step, current="step1")

        self.assertEqual( ("step1", step1), 
                          self.wizard_manager.get_previous_step(current="step2"))

        self.assertEqual( ("step2", step2), 
                          self.wizard_manager.get_previous_step(current="step3"))

 

    def tearDown(self):
        self.patch.stop()


class WizardMiddlewareTest(TestCase):

    def setUp(self):
        self.wizard = models.Wizard.get_instance()

    def test_not_used(self):
        self.wizard.completed = True
        self.wizard.save()
        with mock.patch("nimbus.wizard.middleware.bacula") as bacula:
            self.assertRaises( middleware.MiddlewareNotUsed,
                               middleware.Wizard)
            bacula.unlock_bacula_and_start.assert_called_with()


    def test_load_steps(self):
        mock_import = mock.Mock()
        middleware.__import__ = mock_import
        wizard_middleware = middleware.Wizard()
        mock_import.assert_any_call("nimbus.timezone.views")
        mock_import.assert_any_call("nimbus.network.views")
        mock_import.assert_any_call("nimbus.offsite.views")
        mock_import.assert_any_call("nimbus.session.views")
        mock_import.assert_any_call("nimbus.config.views")
        del middleware.__import__


    def test_restricted_url(self):
        wizard_middleware = middleware.Wizard()
        request = mock.Mock()
        request.META = {"PATH_INFO" : "/wizard"} 
        self.assertFalse( wizard_middleware.is_restricted_url(request))

        request.META = {"PATH_INFO" : "/media"} 
        self.assertFalse( wizard_middleware.is_restricted_url(request))

        request.META = {"PATH_INFO" : "/recovery"} 
        self.assertFalse( wizard_middleware.is_restricted_url(request))

        request.META = {"PATH_INFO" : "ajax"} 
        self.assertFalse( wizard_middleware.is_restricted_url(request))

        request.META = {"PATH_INFO" : "/"} 
        self.assertTrue( wizard_middleware.is_restricted_url(request))


    def test_process_request(self):
        request = mock.Mock()
        request.META = {"PATH_INFO" : "/"}
        wizard_middleware = middleware.Wizard()
        self.wizard.completed = True
        self.wizard.save()
        self.assertEqual( wizard_middleware.process_request(request), None)

        self.wizard.completed = False
        self.wizard.save()
        response = wizard_middleware.process_request(request)
        self.assertNotEqual(response , None)
        self.assertEqual( response._headers['location'][1], "/wizard/start/")
