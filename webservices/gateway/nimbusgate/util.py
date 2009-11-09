#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import logging
import logging.config
import ConfigParser
import signal

LOGGING_CONF = "/etc/nimbus/logging.conf"
NIMBUS_GATEWAY_CONF = "/etc/nimbus/nimbus_gateway.conf"



class FileNotFound(Exception):
    pass


def has_config():
    return os.access(NIMBUS_GATEWAY_CONF, os.R_OK)


def load_logging_system(logfile = LOGGING_CONF):
    logging.config.fileConfig(LOGGING_CONF)


def load_config():
    if has_config():
        config = ConfigParser.ConfigParser()
        config.read(NIMBUS_GATEWAY_CONF)
        return config
    else:
        logger = logging.getLogger(__name__)
        logger.error("Arquivo de configuração do nimbusgateway ausente!")
        raise FileNotFound("Arquivo de configuracao do nimbusgateway ausente!")
    return None




