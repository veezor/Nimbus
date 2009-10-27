#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import logging
import logging.config
import shutil
import ConfigParser
import signal

NIMBUSCONF = "/etc/nimbus/nimbus_manager.conf"


logger = logging.getLogger(__name__)

def has_config():
    try :
        ok = os.access(NIMBUSCONF, os.R_OK)
        return ok
    except IOError:
        return False


def load_logging_system():
    logging.config.fileConfig("/etc/nimbus/logging.conf")


def load_config():
    if has_config():
        config = ConfigParser.ConfigParser()
        config.read("/etc/nimbus/nimbus_manager.conf")
        return config
    else:
        logger.error("Arquivo de configuração do nimbusmanager ausente!")
    return None



def get_config():
    if not get_config.memo:
        get_config.memo = load_config()
    return get_config.memo
get_config.memo = None



def make_backup(filename):
    logger.info("Arquivo de backup criado para %s." % filename)
    try:
        shutil.copy(filename, filename + ".nimbus-bkp")
    except IOError, e:
        pass


def kill_older_manager():
    try: 
        config = get_config()
        pidfile = config.get("PATH","pid")
        pid = file(pidfile).read()
        pid = int(pid)
        logger.warning("Enviando SIGKILL ao daemon")
        os.kill(pid, signal.SIGKILL)
    except (ValueError, IOError), e:
        logger.warning("Arquivo de pid vazio")
    except OSError, e:
        logger.info("Nenhum manager rodando")

