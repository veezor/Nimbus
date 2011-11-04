#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.graphics.models import resource
import systeminfo


@resource
def disk_usage(last_value, last_timestamp):
    diskinfo = systeminfo.DiskInfo("/")
    diskusage = diskinfo.get_used()
    return diskusage
