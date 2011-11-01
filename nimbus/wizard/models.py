#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models
from nimbus.base.models import UUIDSingletonModel as BaseModel
from nimbus.config.models import Config
from nimbus.network.models import NetworkInterface
from nimbus.timezone.models import Timezone
from nimbus.libs import bacula


class Wizard(BaseModel):
    completed = models.BooleanField(default = False)

    def __unicode__(self):
        return u"Wizard(completed=%d)" % self.completed

    @classmethod
    def has_completed(cls):
        return cls.get_instance().completed
    
    def finish(self):
        self.completed = True
        self.save()
        bacula.unlock_bacula_and_start()



class WizardManager(object):

    def __init__(self):
       self.steps = {} 
       self.positions = {}
       self.reversed_positions = {}
       self.pendings = {}


    def __iter__(self):
        return self.get_ordered_steps()

    def get_next_step(self, current):
        pass
    
    def get_steps(self):
        return self.steps.keys()

    def get_ordered_steps(self):
        keys = sorted(self.reversed_positions.keys())
        return [ self.reversed_positions[k] for k in keys ]

    def _add_step_at_position(self, step, position):

        if position in self.reversed_positions:
            raise WizardStepError("Already exist a step at position")

        if step in self.positions:
            raise WizardStepError("Step already added")

        self.positions[step] = position
        self.reversed_positions[position] = step


    def _get_next_position(self):
        return max(self.reversed_positions.keys()) + 1


    def add_step(self, step, requires=None, name=None):

        if name is None:
            name = step.__name__

        if not requires is None:
            if not requires in self.pendings:
                self.pendings[requires] = {}

            self.pendings[requires][name] = step
            return
