# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
import os
import string


###
###   Auxiliar Definitions
###


def merge_dicts(main_dict, *dicts_list):
    """Merge one dict with a list of dicts."""
    for dict in dicts_list:
        main_dict.update(dict)
    return main_dict        

def store_location(request):
    """Stores current user location"""
    request.session["location"] = request.build_absolute_uri()

def redirect_back_or_default(request, default, except_pattern=None):
    """Redirects user back or to a given default place
    unless default place matches an except_pattern
    """
    if "location" in request.session:
        import re
        
        if except_pattern:
            if re.search(except_pattern,request.session["location"]):
                del(request.session["location"]) # use default location
        else:   
            # Try to find redirect error
            referer_full_path = request.META['HTTP_REFERER']
            request_path = request.META['PATH_INFO']
            slice_path_re = 'https?://(www\.)?[\w\d\-_ ]+?(:\d+)?(?P<short_path>/.*)'
            try: 
                referer_path = re.search(slice_path_re,referer_full_path).group('short_path')
                if re.search(referer_path, request_path):
                    del(request.session["location"]) # use default location
            except Exception:
                pass
    redirect = ("location" in request.session) and request.session["location"] or default
    return HttpResponseRedirect(redirect)


def root_path(request):
    """Return root path."""
    return "%s/" % (request.META['SCRIPT_NAME'])
    
def login_path(request):
    """Returns login path."""
    return "%s/session/new" % (request.META['SCRIPT_NAME'])

def computer_path(request, computer_id):
    """Returns computer path."""
    return "%s/computer/%s" % (request.META['SCRIPT_NAME'],computer_id)

def storage_path(request, storage_id):
    """Returns storage path."""
    return "%s/storage/%s" % (request.META['SCRIPT_NAME'], storage_id)

def procedure_path(request, procedure_id, computer_id):
    """Returns procedure path."""
    return "%s/computer/%s/procedure/%s" % (request.META['SCRIPT_NAME'],computer_id,procedure_id)

def schedule_path(request, schedule_id, procedure_id, computer_id):
    """Returns schedule path."""
    return "%s/computer/%s/procedure/%s/schedule/%s" % (request.META['SCRIPT_NAME'],computer_id,procedure_id,schedule_id)

def edit_config_path(request):
    """Returns edit config path."""
    return "%s/config/edit" % (request.META['SCRIPT_NAME'])

def new_device_path(request):
    """Returns new device path."""
    return "%s/config/devices/edit" % (request.META['SCRIPT_NAME'])
        
def new_restriction_path(request):
    """Returns new restriction path."""        
    return "%s/config/restrictions/edit" % (request.META['SCRIPT_NAME'])

def new_offsite_path(request):
    """Returns new offsite path."""        
    return "%s/config/offsite/edit" % (request.META['SCRIPT_NAME'])

# Passo 1
def restore_computer_path(request, computer_id):
    """Returns restore computer path."""
    return "%s/computer/%s/restore/new" % (request.META['SCRIPT_NAME'], computer_id)

# Passo 2
def restore_procedure_path(request, computer_id, procedure_id):
    """Returns restore procedure path."""
    return "%s/computer/%s/procedure/%s/restore/new" % (request.META['SCRIPT_NAME'], computer_id,procedure_id)


# Passo 2
def backup_computer_path(request, computer_id):
    """Returns backup computer path."""
    return "%s/computer/%s/backup/new" % (request.META['SCRIPT_NAME'], computer_id)

# Passo 3
def backup_procedure_path(request, computer_id, procedure_id):
    """Returns backup computer path."""
    return "%s/computer/%s/procedure/%s/backup/new" % (request.META['SCRIPT_NAME'], computer_id, procedure_id)

# Inicio
def backup_path(request):
    """Returns backup computer path."""
    return "%s/backup/new" % (request.META['SCRIPT_NAME'])


def random_password(size):
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
            # Leave
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def remove_or_leave(filepath):
    "remove file if exists"
    try:
        os.remove(filepath)
    except os.error:
        # Leave
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
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_dir)

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
