#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import xmlrpclib
from functools import wraps
from pybacula import BConsoleInitError


from django.conf import settings

from nimbus.libs.bacula import Bacula
from nimbus.shared.middlewares import ThreadPool



def force_baculadir_restart():
    try:
        logger = logging.getLogger(__name__)
        manager = xmlrpclib.ServerProxy(settings.NIMBUS_MANAGER_URL)
        stdout = manager.director_restart()
        logger.info(stdout)
    except Exception, error:
        logger.error("Reload bacula-dir error")



def call_reload_baculadir():
    try:
        logger = logging.getLogger(__name__)
        logger.info("Iniciando comunicacao com o bacula")
        bacula = Bacula()
        bacula.reload()
        logger.info("Reload no bacula executado com sucesso")
        del bacula
    except BConsoleInitError, e:
        force_baculadir_restart()
        logger.error("Comunicação com o bacula falhou")



def connect_on(function, model, signal):

    @wraps(function)
    def function_wrapper(sender, instance, signal, *args, **kwargs):
        value = function(instance)
        Pool = ThreadPool.get_instance()
        if Pool:
            Pool.add_job( call_reload_baculadir, (), {} )
        return value

    signal.connect(function_wrapper, sender=model, weak=False)



