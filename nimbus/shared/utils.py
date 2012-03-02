#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string
import xmlrpclib
from random import choice


from django.conf import settings


class Referer(object):
    def __init__(self, request):
        self.raw = request.META.get('HTTP_REFERER')
        if self.raw:
            self.local = self.local_address()
        else:
            self.local = ''
    
    def local_address(self):
        if self.raw.startswith('http://'):
            return '/' + '/'.join(self.raw.replace('http://','').split('/')[1:])



def filesizeformat(bytes, unit=""):
    
    bytes = float(bytes)
    KB = 1024
    MB = 1024*KB
    GB = 1024*MB
    TB = 1024*GB
    if unit:
        if unit == "B":
            return "%.2f bytes" % bytes
        elif unit == "KB":
            return "%.2f Kb" % (bytes/KB)
        elif unit == "MB":
            return "%.2f Mb" % (bytes/MB)
        elif unit == "GB":
            return "%.2f Gb" % (bytes/GB)
        elif unit == "TB":
            return "%.2f Tb" % (bytes/TB)
        else:
            return bytes
    else:
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

def project_port(request):
    return (':%s' % request.META['SERVER_PORT']) if request.META.get('SERVER_PORT') else ''



def get_nimbus_manager():
    return xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
