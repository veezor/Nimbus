#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import string
from random import choice
from itertools import izip

from django.conf import settings

def filesizeformat(bytes):
    bytes = float(bytes)

    KB = 1024
    MB = 1024*KB
    GB = 1024*MB
    TB = 1024*GB

    if bytes < KB:
        return "%.2f bytes" % bytes

    elif bytes < MB:
        return "%.2f Kb" % (bytes/KB)
    elif bytes < GB:
        return "%.2f Mb" % (bytes/MB)
    elif bytes < TB:
        return "%.2f Gb" % (bytes/GB)
    else:
        return "%.2f Tb" % (bytes/TB)


def int_or_string(value):
    try:
        return int(value)
    except ValueError, error:
        return value

    
def dict_from_querydict(querydict, lists=()):
    d = {}
    for key, value in querydict.items():
        newkey = key.replace(".","_")

        if not newkey in lists:
            newvalue = int_or_string(value)
        else:
            newvalue = querydict.getlist(key)
            newvalue = [ int_or_string(x) for x in newvalue ]
        
        d[newkey] = newvalue

    return d


def ordered_dict_value_to_formatted_float(dictionary):
    return [ ("%.2f" % v) for k,v in sorted( dictionary.items() ) ]


def bytes_to_mb(size):
    return size/1024.0/1024

def random_password(size=20):
    """Generates random password of a given size."""
    return ''.join([choice(string.letters + string.digits) for i in range(size)])
    
    



###
###   File Handling Specific Definitions
###


def remove_or_leave(filepath):
    "remove file if exists"
    try:
        os.remove(filepath)
    except os.error:
        pass


def mount_path(filename,rel_dir):
    "mount absolute dir path and filepath"
    filename = str(filename).lower()
    base_dir = absolute_dir_path(rel_dir)
    filepath = absolute_file_path(filename, rel_dir)
    return base_dir, filepath
    
    
def absolute_file_path(filename, rel_dir):
    """Return full path to a file from script file location and given directory."""
    root_dir = absolute_dir_path(rel_dir)
    return os.path.join(root_dir, filename)


def absolute_dir_path(rel_dir):
    """Return full path to a directory from script file location."""
    return os.path.join(settings.NIMBUS_CUSTOM_DIR, rel_dir)


def isdir(path):
    if path.endswith('/'):
        return True
    else:
        return False


def get_filesize_from_lstat(lstat):
    b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    val = 0
    size = lstat.split(' ')[7] # field 7
    for i,char in enumerate(size):
        r = (b64.find(char)) * (pow(64,(len(size)-i)-1))
        val += r
    return val


def project_port(request):
    return (':%s' % request.META['SERVER_PORT']) if request.META['SERVER_PORT'] else ''

