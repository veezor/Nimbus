#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
from django.test import TestCase

from nimbus.wizard import models, admin


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
        pass

    def tearDown(self):
        self.patch.stop()
