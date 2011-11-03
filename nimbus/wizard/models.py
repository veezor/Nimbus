#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models
from nimbus.base.models import UUIDSingletonModel as BaseModel
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


class WizardStepError(Exception):
    pass



class WizardManager(object):

    def __init__(self):
        self.steps = {}
        self.at_begin_steps = {}
        self.at_begin_positions = {}
        self.at_begin_reversed_positions = {}
        self.at_end_steps = {}
        self.at_end_positions = {}
        self.at_end_reversed_positions = {}
        self.without_position_steps = {}
        self.without_position_steps_order = []

    def __iter__(self):
        return self.get_steps()

    def get_next_step(self, current):
        return self._get_neighbor_step(current, 1)

    def get_previous_step(self, current):
        return self._get_neighbor_step(current, -1)

    def _get_neighbor_step(self, current, shift):
        try:
            steps = self.get_steps()
            index = steps.index(current)

            if index + shift < 0:
                raise IndexError

            name = steps[index+shift]
            return name,self.steps[name]
        except IndexError:
            raise WizardStepError("step not found")

    def get_step(self, name):
        return self.steps[name]
    
    def get_steps(self):
        at_begin = self._get_ordered_steps(self.at_begin_reversed_positions)
        without_position = self._get_ordered_steps(self.without_position_steps)
        at_end = self._get_ordered_steps(self.at_end_reversed_positions)
        return at_begin + without_position + at_end

    def _get_ordered_steps(self, store):

        if store is self.without_position_steps:
            return self.without_position_steps_order
        elif store is self.at_begin_reversed_positions:
            keys = sorted(store.keys())
        else:
            keys = reversed(sorted(store.keys()))
        return [ store[k] for k in keys ]


    def _add_step_at_position(self, step, position, store, reversed_store, name):

        if position in reversed_store:
            raise WizardStepError("Already exist a step at position")

        if step in store:
            raise WizardStepError("Step already added")

        store[step] = position
        reversed_store[position] = name



    def _add_without_position_step(self, step, name=None):
        name = self._add_step(step, self.without_position_steps, name)
        self.without_position_steps_order.append(name)


    def _add_step(self, step, store, name=None):
        if name in store:
            raise WizardStepError("Step already added")
        
        store[name] = step
        self.steps[name] = step

        return name


    def _add_step_at_begin(self, step, position, name=None):
        self._add_step_at_position(step, position,
                                   self.at_begin_positions,
                                   self.at_begin_reversed_positions,
                                   name)
        self._add_step(step, self.at_begin_steps, name)



    def _add_step_at_end(self, step, position, name=None):
        position = position * -1
        self._add_step_at_position(step, position,
                                   self.at_end_positions,
                                   self.at_end_reversed_positions,
                                   name)
        self._add_step(step, self.at_end_steps, name)


    def add_step(self, step, position=None, name=None):

        if name is None:
            name = step.__name__

        if not position is None:
            if position >= 0:
                self._add_step_at_begin(step, position, name)
            else:
                self._add_step_at_end(step, position, name)
        else:
            self._add_without_position_step(step, name)



wizard_manager = WizardManager()


def add_step(position=None, name=None):

    def inner(function):
        wizard_manager.add_step(function, position, name)
        return function

    return inner
