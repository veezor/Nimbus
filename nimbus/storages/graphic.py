#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.graphics.models import resource, filter, filter_value, Data
import systeminfo


@resource
def disk_usage(manager, interactive):
    u"""Uso de disco"""
    diskinfo = systeminfo.DiskInfo("/")
    diskusage = diskinfo.get_used()
    return diskusage


@filter_value
def convert_data_to_gb(resource_name, data):
    if resource_name == "disk_usage":
        value = data.value/1024.0/1024
        return Data(value, data.timestamp)
    else:
        return data


@filter
def duplicate_unary_list(resource_name, data_list):
    return data_list * 2
