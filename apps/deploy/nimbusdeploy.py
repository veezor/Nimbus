#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, shutil, sys
from os.path import join
import logging
import logging.handlers
import mercurial.commands
import mercurial.ui
import mercurial.hg
import subprocess



NIMBUS_VAR_PATH = "/var/nimbus/"
NIMBUS_HG_PATH = NIMBUS_VAR_PATH + "hg/"
NIMBUS_CUSTOM_PATH = NIMBUS_VAR_PATH + "custom/"
NIMBUS_HG_URL = "http://hg.linconet.com.br/bc-devel"
NIMBUS_ETC_PATH = "/etc/nimbus"
NIMBUS_LOG_PATH = "/var/log/nimbus"


logger = None

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler_sysout = logging.StreamHandler(sys.stdout)
    handler_syslog = logging.handlers.SysLogHandler('/dev/log')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler_sysout.setFormatter(formatter)
    handler_syslog.setFormatter(formatter)
    logger.addHandler(handler_sysout)
    logger.addHandler(handler_syslog)


def log_exception(func):

    def wrapper(*args,**kwargs):
        try:
            func(*args, **kwargs)
        except Exception, e:
            logger.exception(e)
            sys.exit(1)

    wrapper.__name__ = func.__name__
    return wrapper


@log_exception
def make_dir(dirname):
    logger.info('creating directory %s' % dirname)
    os.mkdir(dirname) 
    logger.info('directory %s created' % dirname)


def make_dirs():
    make_dir(NIMBUS_LOG_PATH)
    make_dir(NIMBUS_ETC_PATH)
    make_dir(NIMBUS_VAR_PATH)


@log_exception
def get_new_nimbus_version():
    ui = mercurial.ui.ui()
    mercurial.commands.clone(ui, NIMBUS_HG_URL, dest=NIMBUS_HG_PATH)


@log_exception
def has_nimbus():
    return os.access(NIMBUS_VAR_PATH)


@log_exception
def move_custom():
    os.rename( join(NIMBUS_HG_PATH, "custom"), NIMBUS_CUSTOM_PATH)


@log_exception
def install_config_files():
    shutil.copy( join(NIMBUS_HG_PATH, "webservices/gateway/nimbus_gateway.conf"),
                 NIMBUS_ETC_PATH )
    shutil.copy( join(NIMBUS_HG_PATH, "django/backup_corporativo/logging.conf"),
                 NIMBUS_ETC_PATH )
    shutil.copy( join(NIMBUS_HG_PATH, "django/backup_corporativo/settings_sample.py"),
                 join(NIMBUS_HG_PATH, "django/backup_corporativo/settings.py"))



@log_exception
def check_user():
    f = file("/etc/passwd")
    for line in f:
        user = line.split(':')[0]
        if user == "nimbus":
            f.close()
            return True
    f.close()
    return False



@log_exception
def create_user():
    cmd = subprocess.Popen( ["/usr/sbin/adduser",
                             "--no-create-home",
                             "--disabled-password",
                             "--disabled-login",
                             "nimbus"] )
    return not bool(cmd.wait())



@log_exception
def chown_nimbus_files():
    
    def callback(arg, dirname, fnames):
        for file in fnames:
            os.chown(os.path.join(dirname, file), 'nimbus', 'nimbus')

    os.path.walk(NIMBUS_VAR_PATH, callback, None)
    os.path.walk(NIMBUS_ETC_PATH, callback, None)


@log_exception
def update_nimbus_version():
    ui = mercurial.ui.ui()
    ui.readconfig(os.path.join(NIMBUS_HG_PATH, ".hg/hgrc"))
    repo = mercurial.hj.repository(ui, path=NIMBUS_HG_PATH)
    mercurial.commands.pull(ui, repo)
    mercurial.commands.update(ui, repo)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
