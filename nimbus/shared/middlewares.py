#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import traceback

class AjaxDebug(object):

    def process_exception(self, request, exception):
        traceback.print_exc()
