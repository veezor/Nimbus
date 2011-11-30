#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# SCRIPT PARA DEPLOY DO NIMBUS
# Está bem estruturadozão mesmo

from sys import argv, exit
import re
import shutil
import os
import imp
import codecs



product_apps = {'professional': ['nimbus.offsite'],
                'opensource': []}
base_dirs = ['nimbus/libs', 'nimbus/media', 'nimbus/remotestorages',
             'nimbus/confs', 'nimbus/binary', 'nimbus/graphics',
             'nimbus/shared', 'nimbus/build', 'nimbus/statistics']

garbage = ['.pyc', 'DS_Store', 'header_py.txt', 'header_js.txt', 'deploy.py']

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

def find_files(where, exten):
    result = []
    for root, dirs, files in os.walk(where):
        for filename in files:
            fullfilename = os.path.join(root, filename)
            if fullfilename.endswith(exten):
                result.append(fullfilename)
    return result

def delete_garbage(where):
    for exten in garbage:
        files = find_files(where, exten)
        for f in files:
            os.remove(f)
            
def put_py_header(where):

    with codecs.open('header_py.txt', encoding='UTF-8') as h:
        header = h.read()
    
    files = find_files(where, ".py")
    for filename in files:
        with codecs.open(filename, encoding='UTF-8') as f:
            content = f.read()
            content = content.replace("#!/usr/bin/env python", "")
            content = content.replace("# -*- coding: UTF-8 -*-", "")
            content = header + "\n" + content

        with codecs.open(filename, "w", encoding='UTF-8') as f:
            f.write(content)

def js_except_files(filelist):
    result = []
    for filepath in filelist:
        filename = filepath.split('/')[-1]
        if filename.lower().startswith('jquery') or filename.lower().startswith('jqplot'):
            pass
        else:
            result.append(filepath)
    return result

def put_js_header(where):
    with codecs.open('header_js.txt', encoding='UTF-8') as h:
        header = h.read()
    
    allfiles = find_files(where, ".js")
    files = js_except_files(allfiles)
    for filename in files:
        with codecs.open(filename, encoding='UTF-8') as f:
            content = f.read()
            content = header + "\n" + content
    
        with codecs.open(filename, "w", encoding='UTF-8') as f:
            f.write(content)
    

dst = '../../deploy_tmp'
print "Definindo produto:"
product = set_product()
print "Produto: %s" % product.upper()
print "Copiando arquivos"
copy_files(dst)
print "Arquivos copiados"
print "Criando arquivo de configuração"
create_settings_py(product, "%s/nimbus/%s" % (dst, 'settings.py'))
print "settings.py criado"
print "Removendo APPS desnecessárias"
remove_unused(dst)
print "Removendo lixo"
delete_garbage(dst)
if product == 'opensource':
    print "Adicionando licenças aos arquivos Python"
    put_py_header(dst)
    print "Adicionando licenças aos arquivos JavaScript"
    put_js_header(dst)