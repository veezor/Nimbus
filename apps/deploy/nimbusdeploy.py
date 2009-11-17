#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, shutil
from os.path import join

from deploylib import rule, start # deploylib has logging configure

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


logger = logging.getLogger(__name__)




def make_dir(dirname):
    logger.info('creating directory %s' % dirname)
    os.mkdir(dirname) 
    logger.info('directory %s created' % dirname)


@rule
def make_dirs():
    make_dir(NIMBUS_LOG_PATH)
    make_dir(NIMBUS_ETC_PATH)
    make_dir(NIMBUS_VAR_PATH)
    return True


@rule(depends=make_dirs)
def get_new_nimbus_version():
    ui = mercurial.ui.ui()
    mercurial.commands.clone(ui, NIMBUS_HG_URL, dest=NIMBUS_HG_PATH)
    return True



@rule(depends=get_new_nimbus_version)
def install_config_files():
    os.rename( join(NIMBUS_HG_PATH, "custom"), NIMBUS_CUSTOM_PATH)
    shutil.copy( join(NIMBUS_HG_PATH, "webservices/gateway/nimbus_gateway.conf"),
                 NIMBUS_ETC_PATH )
    shutil.copy( join(NIMBUS_HG_PATH, "django/backup_corporativo/logging.conf"),
                 NIMBUS_ETC_PATH )
    shutil.copy( join(NIMBUS_HG_PATH, "django/backup_corporativo/settings_sample.py"),
                 join(NIMBUS_HG_PATH, "django/backup_corporativo/settings.py"))
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
    f = file("/etc/passwd")
    for line in f:
        user = line.split(':')[0]
        if user == "nimbus":
            f.close()
            return True
    f.close()
    return False




@rule( depends=(install_config_files, check_user) )
def chown_nimbus_files():
    
    def callback(arg, dirname, fnames):
        for filename in fnames:
            os.chown(os.path.join(dirname, filename), 'nimbus', 'nimbus')

    os.path.walk(NIMBUS_VAR_PATH, callback, None)
    os.path.walk(NIMBUS_ETC_PATH, callback, None)
    return True


@rule(depends=chown_nimbus_files) #depends use reverse order
def install_nimbus(): # for semantic way, bypass to chown_nimbus_files
    return True


@rule(on_failure=install_nimbus)
def has_nimbus():
    return not os.access(NIMBUS_VAR_PATH)


@rule(depends=has_nimbus)
def update_nimbus_version():
    ui = mercurial.ui.ui()
    ui.readconfig(os.path.join(NIMBUS_HG_PATH, ".hg/hgrc"))
    repo = mercurial.hg.repository(ui, path=NIMBUS_HG_PATH)
    mercurial.commands.pull(ui, repo)
    mercurial.commands.update(ui, repo)
    return True



#@rule(depends=update_nimbus_version)
@rule
def deploy():
    logger.info("Nimbus deploy finalized")
    return True

start(deploy)
