#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
import os
from backup_corporativo.settings import MAIN_APP

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404 
from django.shortcuts import redirect as _redirect
from django.core.urlresolvers import reverse as _reverse

from backup_corporativo import settings


### Routing ###
def reverse(viewname, args=None, kwargs=None):
    return _reverse( "%s.views.%s" % (MAIN_APP, viewname) , args=args, kwargs=kwargs)


def redirect(viewname, *args, **kwargs):
    path = reverse(viewname, *args, **kwargs)
    return HttpResponseRedirect(path)


###
###   Auxiliar Definitions
###

def get_settings_dict():
    settings_dict = dict()
    items = [
        'BACULA_DATABASE_USER',
        'BACULA_DATABASE_PASSWORD',
        'BACULA_DATABASE_NAME',
        'BACULA_DATABASE_HOST',
        'BACULA_DATABASE_PORT']

    for i in items:
        settings_dict.update([[i, getattr(settings, i)]])
    return settings_dict


#TODO migrar para usar apenas reverse e url
def new_computer_backup(comp_id, request, wizard=False):
    script_name = request.META['SCRIPT_NAME']
    location = "%s/computer/%s/backup/new" % (script_name, comp_id,)
    if wizard:
        location += "?wizard=%s" % wizard
    return location


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


# Passo 1
def restore_computer_path(request, computer_id):
    """Returns restore computer path."""
    return "%s/computer/%s/restore/new" % (request.META['SCRIPT_NAME'], computer_id)


# Passo 2
def restore_procedure_path(request, computer_id, procedure_id):
    """Returns restore procedure path."""
    return "%s/computer/%s/procedure/%s/restore/new" % (request.META['SCRIPT_NAME'], computer_id,procedure_id)

    
def random_password(size=20):
    """Generates random password of a given size."""
    import string
    from random import choice
    return ''.join([choice(string.letters + string.digits) for i in range(size)])
    
    
def dictfetch(cursor):
    """Returns a list with dicts of an unfetched cursor"""
    from itertools import izip
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
            #TODO: ajeitar
            raise


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
    return os.path.join(os.path.dirname(os.path.abspath(settings.NIMBUS_CUSTOM_PATH)), rel_dir)


def isdir(path):
    if path.endswith('/'):
        return True
    else:
        return False


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
        
        #print file_path, file_name
        
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
      
CERTIFICATE_CONFIG_PATH = absolute_file_path('certificate.conf','custom/crypt')
