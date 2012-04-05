#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import re
import logging
import traceback
import logging.config

from django.conf import settings
from backgroundjobs import ThreadPool as BJThreadPool
from django.utils.translation import ugettext_lazy as _






class LogSetup(object): # on bootstrap

    def __init__(self):
        logging.config.fileConfig(settings.LOGGING_CONF)
        pass



class ThreadPool(object):

    instance = None

    def __init__(self):
        if not self.instance:
            self.__class__.instance = BJThreadPool()


    @classmethod
    def get_instance(cls):
        return cls.instance




class AjaxDebug(object):

    def process_exception(self, request, exception):
        traceback.print_exc(file=sys.stderr)
        logger = logging.getLogger(__name__)
        logger.exception(_(u"Exception raised from django"))
