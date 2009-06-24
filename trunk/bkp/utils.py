# Misc
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404


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
    return "%s/device/new" % (request.META['SCRIPT_NAME'])


def absolute_file_path(filename, rel_dir):
    """Return full path to a file from script file location and given directory."""
    root_dir = absolute_dir_path(rel_dir)
    return os.path.join(root_dir, filename)


def absolute_dir_path(rel_dir):
    """Return full path to a directory from script file location."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_dir)

def remove_or_leave(filepath):
    """Remove file if exists."""
    try:
        os.remove(filepath)
    except os.error:
        # Leave
        pass
        
def random_password(size):
    """Generates random password of a given size."""
    import string
    from random import choice
    return ''.join([choice(string.letters + string.digits) for i in range(size)])