#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# SCRIPT PARA DEPLOY DO NIMBUS
# Está bem estruturadozão mesmo

from sys import argv, exit
import re
import shutil
import os
import imp



product_apps = {'professional': ['nimbus.offsite'],
                'opensource': []}
base_dirs = ['nimbus/libs', 'nimbus/media', 'nimbus/remotestorages',
             'nimbus/confs', 'nimbus/binary', 'nimbus/graphics',
             'nimbus/shared', 'nimbus/build', 'nimbus/statistics']

def change_setting(settings, regex, new_value):
    match = re.search(regex, settings, re.DOTALL)
    if match:
        return settings.replace(match.group(1), new_value)
    else:
        print "Ocorreu algum problema rescrevendo o settings.py"
        exit(1)

def set_product():
    if (len(argv) < 2) or (argv[1] not in ['professional', 'opensource']):
        print "Use:\n python deploy.py professional\nOU\n python deploy.py opensource"
        exit(1)
    else:
        return argv[1]

def create_settings_py(product, output_file='settings.py'):
    s = open('settings_executable.py')
    settings = s.read()
    s.close()

    settings = change_setting(settings,
                   "(MODULAR\_APPS\s*\=\s*\[.*?\])",
                   "MODULAR_APPS = ['%s']" % "', '".join(product_apps[product]))

    settings = change_setting(settings,
                  '(NIMBUS\_PRODUCT\s*\=\s*\"[a-z]+\")',
                  'NIMBUS_PRODUCT = "%s"' % product)

    settings_py = open(output_file, 'w')
    settings_py.write(settings)

def dirs_to_remove(destination):
    # from settings import INSTALLED_APPS
    s = imp.load_source('INSTALLED_APPS', "%s/nimbus/settings.py" % destination)
    INSTALLED_APPS = s.INSTALLED_APPS
    print INSTALLED_APPS
    dirs = base_dirs[:]
    for app in INSTALLED_APPS:
        if app.startswith('nimbus.'):
            dirs.append(app.replace(".","/"))
    all_dirs = []
    for d in os.listdir(destination + "/nimbus"):
        if os.path.isdir(d):
            all_dirs.append(d)
    result = []
    for d in all_dirs:
        if "nimbus/%s" % d not in dirs:
            result.append("nimbus/%s" % d)
    print result
    return result

def copy_files(destination='../../deploy_tmp'):
    try:
        shutil.rmtree(destination)
    except:
        pass
    shutil.copytree('../../nimbus/', destination)

def remove_unused(destination):
    for d in dirs_to_remove(destination):
        shutil.rmtree("%s/%s" % (destination, d))



product = set_product()
dst = '../../deploy_tmp'
copy_files(dst)
create_settings_py(product, "%s/nimbus/%s" % (dst, 'settings.py'))
remove_unused(dst)