#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import string
from random import choice
from itertools import izip

from django.conf import settings


def pathdepth(path):
    depth = path.count("/")

    if path.endswith("/"):
        depth -=  1

    return depth



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


def new_procedure_schedule(proc_id, request, type='Weekly', wizard=False):
    script_name = request.META['SCRIPT_NAME']
    location = "%s/procedure/%s/schedule/new" % (script_name, proc_id)
    location += "?type=%s" % type
    if wizard:
        location += "&wizard=%s" % wizard
    return  location


def schedule_inverse(type):
    if type == 'Weekly':
        return 'Monthly'
    elif type == 'Monthly':
        return 'Weekly'



def ordered_dict_value_to_formatted_float(dictionary):
    return [ ("%.2f" % v) for k,v in sorted( dictionary.items() ) ]


def bytes_to_mb(size):
    return size/1024.0/1024

def random_password(size=20):
    """Generates random password of a given size."""
    return ''.join([choice(string.letters + string.digits) for i in range(size)])
    
    
def dictfetch(cursor):
    """Returns a list with dicts of an unfetched cursor"""
    col_names = [desc[0] for desc in cursor.description]
    result = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        result.append(row_dict)
    return result


###
###   Time Handling Specific Definitions
###


def current_time(uct=False):
    if uct:
        time_function = time.gmtime
    else:
        time_function = time.localtime
    return time.strftime("%d-%m-%Y %H:%M:%S", time_function())


###
###   File Handling Specific Definitions
###


def create_or_leave(dirpath):
    "create dir if dont exists"
    try:
        os.makedirs(dirpath)
    except OSError:
        if os.path.isdir(dirpath):
            pass
        else:
            #TODO: adicionar entrada no log
            pass


def remove_or_leave(filepath):
    "remove file if exists"
    try:
        os.remove(filepath)
    except os.error:
        pass


def prepare_to_write(filename,rel_dir,mod="w",remove_old=False):
    "make sure base_dir exists and open filename"
    base_dir,filepath = mount_path(filename,rel_dir)
    create_or_leave(base_dir)
    if remove_old:
        remove_or_leave(filepath)
    return open(filepath, mod)


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


#
# Atenção:
#
# Não mude nada aqui a menos
# que tenha absoluta certeza
# do que está fazendo.
#
def parse_filetree(files):
    """
    Parse a list of files creating a new hierarchical data structure.
    
    Dict are for directories and lists are for files.
    # {'var': [{'tmp': ['a']}]}
    
    >>> files = ['/var/tmp/a', '/var/tmp/b', '/etc/httpd/httpd.conf', \
        '/etc/httpd/sites-available/a', '/etc/httpd/sites-available/b', \
        '/var/tmp/lixo', '/usr/contrib/']
    >>> tree = parse_filetree(files)
    >>> assert tree == {'var': [{'tmp': ['a', 'b', 'lixo']}], 'etc': [{'httpd': ['httpd.conf', {'sites-available': ['a', 'b']}]}], 'urs': [{'contrib': []}]}
    """
    file_tree = {}
            
    for f in files:
        f, fid = f.rsplit(':', 1)
        file_path = [x for x in f.split('/') if x]
        if isdir(f):
            file_name = None
        else:
            file_name = '%s:%s' % (file_path.pop(), fid)
        file_path = ['%s/' % x for x in file_path]
                
        local_tree = file_tree
        for n, fp in enumerate(file_path):
            if fp in local_tree:
                local_tree = local_tree[fp]
            else:
                if isinstance(local_tree, list):
                    for i in local_tree:
                        if isinstance(i, dict) and i.has_key(fp):
                            local_tree = i[fp]
                            break
                    else:
                        local_tree.append({fp: []})
                        local_tree = local_tree[-1][fp]
                    if n == len(file_path) - 1 and file_name:
                        local_tree.append(file_name)
                else:
                    local_tree[fp] = []
                    local_tree = local_tree[fp]
                    if n == len(file_path) - 1 and file_name:
                        local_tree.append(file_name)
    return file_tree


def get_filesize_from_lstat(lstat):
    b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    val = 0
    size = lstat.split(' ')[7] # field 7
    for i,char in enumerate(size):
        r = (b64.find(char)) * (pow(64,(len(size)-i)-1))
        val += r
    return val


