#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from functools import wraps
from pybacula import BConsoleInitError
from nimbus.libs.bacula import Bacula



def call_reload():
    try:
        bacula = Bacula()
        bacula.reload()
        del bacula
    except BConsoleInitError, e:
        logger = logging.getLogger(__name__)
        logger.error("Comunicação com o bacula falhou")



def connect_on(function, model, signal):

    @wraps(function)
    def function_wrapper(sender, instance, signal, *args, **kwargs):
        value = function(instance)
        call_reload()
        return value

    signal.connect(function_wrapper, sender=model)
