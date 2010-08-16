#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from functools import wraps
from pybacula import BConsoleInitError


from nimbus.libs.bacula import Bacula
from nimbus.shared.middlewares import ThreadPool







def call_reload_baculadir():
    try:
        logger = logging.getLogger(__name__)
        logger.info("Iniciando comunicacao com o bacula")
        bacula = Bacula()
        bacula.reload()
        logger.info("Reload no bacula executado com sucesso")
        del bacula
    except BConsoleInitError, e:
        logger.error("Comunicação com o bacula falhou")



def connect_on(function, model, signal):

    @wraps(function)
    def function_wrapper(sender, instance, signal, *args, **kwargs):
        value = function(instance)
        Pool = ThreadPool.get_instance()
        Pool.add_job( call_reload_baculadir, (), {} )
        return value

    signal.connect(function_wrapper, sender=model, weak=False)



