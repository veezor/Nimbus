#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from urllib2 import URLError

from nimbus.graphics.models import resource
from nimbus.offsite.models import Offsite


@resource
def offsite(manager, interactive):
    u"""Uso de disco do Offsite"""
    offsite = Offsite.get_instance()
    if offsite.active and not interactive:
        try:
            s3 = Offsite.get_s3_interface()
            return s3.get_usage()
        except URLError, error:
            return 0.0
    else:
        return 0.0




