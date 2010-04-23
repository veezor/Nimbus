#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import logging
import logging.config
from django.conf import settings


logging.config.fileConfig(settings.NIMBUS_LOGCONF)


