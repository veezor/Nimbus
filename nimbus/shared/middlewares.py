#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import logging
import traceback
import logging.config

from django.conf import settings



class LogSetup(object): # on bootstrap

    def __init__(self):
        logging.config.fileConfig(settings.LOGGING_CONF)




class AjaxDebug(object):

    def process_exception(self, request, exception):
        traceback.print_exc(file=sys.stderr)
        logger = logging.getLogger(__name__)
        logger.exception("Exception levantada no django")
