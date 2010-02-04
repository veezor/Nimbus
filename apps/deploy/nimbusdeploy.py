#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, shutil
from os.path import join
import pwd

from deploylib import rule, start # deploylib has logging configure


import sys
import logging
import logging.handlers
import subprocess



NIMBUS_VAR_PATH = "/var/nimbus/"
NIMBUS_HG_PATH = NIMBUS_VAR_PATH + "hg/"
NIMBUS_CUSTOM_PATH = NIMBUS_VAR_PATH + "custom/"
NIMBUS_DEPS_PATH = NIMBUS_VAR_PATH + "deps/"
NIMBUS_HG_URL = "http://hg.devel.linconet.com.br/bc-devel"
NIMBUS_ETC_PATH = "/etc/nimbus"
NIMBUS_LOG_PATH = "/var/log/nimbus"


NIMBUSDEP_ZIP = "nimbusdep.zip"

TRUECRYPT_BIN_PATH = "/usr/bin/truecrypt"


logger = logging.getLogger(__name__)



class RootRequired(Exception):
    pass

class PackageNotFound(Exception):
    pass


def make_dir(dirname):
    logger.info('creating directory %s' % dirname)
    os.mkdir(dirname) 
    logger.info('directory %s created' % dirname)


@rule
def make_dirs():
    make_dir(NIMBUS_LOG_PATH)
    make_dir(NIMBUS_ETC_PATH)
    make_dir(NIMBUS_VAR_PATH)
    make_dir(NIMBUS_DEPS_PATH)
    return True


@rule
def get_new_nimbus_version():
    import mercurial.ui , mercurial.hg, mercurial.commands
    ui = mercurial.ui.ui()
    mercurial.commands.clone(ui, NIMBUS_HG_URL, dest=NIMBUS_HG_PATH)
    return True



@rule(depends=get_new_nimbus_version)
def install_config_files():
    shutil.copytree( join(NIMBUS_HG_PATH, "custom"), NIMBUS_CUSTOM_PATH)
    
    shutil.copy( join( NIMBUS_HG_PATH, 
                       "webservices/gateway/nimbus_gateway.conf"),
                 NIMBUS_ETC_PATH )

    shutil.copy( join( NIMBUS_HG_PATH, 
                       "webservices/manager/nimbus_manager.conf"),
                 NIMBUS_ETC_PATH )


    shutil.copy( join( NIMBUS_HG_PATH, 
                       "webservices/manager/bin/nimbus-manager"),
                 "/usr/local/bin/" )

    shutil.copy( join( NIMBUS_HG_PATH, 
                       "webservices/manager/init.d/nimbusmanager"),
                 "/etc/init.d/" )

    shutil.copy( join(NIMBUS_HG_PATH, "django/backup_corporativo/logging.conf"),
                 NIMBUS_ETC_PATH )
    shutil.copy( join( NIMBUS_HG_PATH, 
                       "django/backup_corporativo/settings_sample.py"),
                 join(NIMBUS_HG_PATH, "django/backup_corporativo/settings.py"))

    shutil.copy( join( NIMBUS_HG_PATH,
                       "django/apacheconf/default"), 
                  "/etc/apache2/sites-enabled/000-default" )
    shutil.copy( join( NIMBUS_HG_PATH,
                       "django/apacheconf/nimbus.wsgi"), 
                  "/usr/lib/cgi-bin/nimbus.wsgi" )
                        
    return True


@rule
def create_user():
    cmd = subprocess.Popen( ["/usr/sbin/adduser",
                             "--no-create-home",
                             "--disabled-password",
                             "--disabled-login",
                             "nimbus"] )
    return not bool(cmd.wait())


@rule(on_failure=create_user)
def check_user():
    try:
        pwd.getpwnam('nimbus')
        return True
    except KeyError, e:
        return False
    


@rule
def database_alert():
    logger.warning( "Não foi possível criar o banco de dados,"\
                     "o mesmo já existe")
    return True


@rule(on_failure=database_alert)
def generate_database():
    import MySQLdb, getpass

    print "Informe a senha de root do mysql: "
    password = getpass.getpass()
    connection = MySQLdb.connect('localhost', "root", password)
    cursor = connection.cursor()
    try:
        cursor.execute("create database nimbus;")
        cursor.execute("GRANT ALL PRIVILEGES ON nimbus.* TO 'nimbus'@'localhost'"\
                       "IDENTIFIED BY 'nimbus'")

    except MySQLdb.ProgrammingError, e:
        return False

    finally:
        cursor.close()
        connection.close()
    return True
    


@rule
def config_settings_dbfile():
    filepath = join(NIMBUS_HG_PATH, "django/backup_corporativo/settings.py")
    content = file(filepath).read()
    print "Por favor, insira a configuracao do BD"
    raw_input("pressione qualquer tecla para continuar....")
    cmd = subprocess.Popen(["vim", filepath])
    cmd.wait()
    if cmd.returncode != 0:
        return False
    return True



@rule(depends=(generate_database, config_settings_dbfile))
def sync_db():
    from django.core.management import call_command
    sys.path.insert(0, "/var/nimbus/hg/django")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backup_corporativo.settings'
    call_command('syncdb')
    return True



@rule( depends=(install_config_files, check_user, sync_db) )
def chown_nimbus_files():
    pwinfo = pwd.getpwnam('nimbus')
    uid = pwinfo.pw_uid
    gid = pwinfo.pw_gid
    
    def callback(arg, dirname, fnames):
        os.chown(dirname, uid, gid)
        for filename in fnames:
            filepath = os.path.join(dirname, filename)
            os.chown(filepath, uid, gid)

    os.path.walk(NIMBUS_VAR_PATH, callback, None)
    os.path.walk(NIMBUS_ETC_PATH, callback, None)
    os.path.walk(NIMBUS_DEPS_PATH, callback, None)
    os.path.walk(NIMBUS_LOG_PATH, callback, None)
    return True




@rule(on_failure='install_nimbus')
def has_nimbus():
    return os.access(NIMBUS_VAR_PATH, os.R_OK)


def check_python_dep(name):
    logger.info('Checking dependency %s' % name)
    try:
        __import__(name)
        logger.info('%s is found.' % name)
        return True
    except ImportError, e:
        logger.error('%s not found.' % name)
        raise ImportError(e)


@rule
def unzip_pythonlibs():
    cmd = subprocess.Popen(["unzip", NIMBUSDEP_ZIP, "-d", NIMBUS_DEPS_PATH])
    cmd.wait()
    return not bool(cmd.returncode)


@rule(depends=unzip_pythonlibs)
def check_python_packages():
    check_python_dep('django')
    check_python_dep('netifaces')
    check_python_dep('M2Crypto')
    return True

@rule
def has_truecrypt():
    return os.access( TRUECRYPT_BIN_PATH , os.R_OK)




@rule
def generate_hgrc_for_root_user():
    f = file("/root/.hgrc","w")
    f.write("[trusted]\nusers = nimbus\ngroups = nimbus\n\n"\
            "[auth]\nnimbus.prefix=%s\nnimbus.username=deploy\n"\
            "nimbus.password=deploy" % NIMBUS_HG_URL)
    f.close()
    return True


@rule( depends=( has_truecrypt,
                 generate_hgrc_for_root_user,
                 make_dirs,
                 check_python_packages,
                 chown_nimbus_files, 
                  )) #depends use reverse order
def install_nimbus(): # for semantic way, bypass to chown_nimbus_files
    return True




def is_installed(package):
    if not package.isInstalled:
        raise PackageNotFound("Package %s not found" % package.name)


@rule
def check_system_dependencies():
    import apt
    cache = apt.cache.Cache()
    is_installed(cache['apache2'])
    is_installed(cache['libapache2-mod-wsgi'])
    is_installed(cache['libapache2-mod-python'])
    is_installed(cache['mysql-server-5.0'])
    return True
    
@rule
def set_python_path():
    sys.path.insert(0, NIMBUS_DEPS_PATH)
    return True


@rule(depends=(has_nimbus, 
               check_system_dependencies))
def update_nimbus_version():

    import mercurial.ui , mercurial.hg, mercurial.commands

    ui = mercurial.ui.ui()
    ui.readconfig(os.path.join(NIMBUS_HG_PATH, ".hg/hgrc"))
    repo = mercurial.hg.repository(ui, path=NIMBUS_HG_PATH)
    mercurial.commands.pull(ui, repo)
    mercurial.commands.update(ui, repo)
    return True



@rule
def check_root_user():
    if os.getuid() != 0:
        raise RootRequired('You must be root')
    return True



@rule(depends=(check_root_user, set_python_path, update_nimbus_version))
def deploy():
    logger.info("Nimbus deploy finalized")
    return True

start(deploy)
