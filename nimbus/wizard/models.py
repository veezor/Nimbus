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
