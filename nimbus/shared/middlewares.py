#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import traceback

class AjaxDebug(object):

    def process_exception(self, request, exception):
        traceback.print_exc()
        logger = logging.getLogger(__name__)
        logger.exception("Exception levantada no django")
