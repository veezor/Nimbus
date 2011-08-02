#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from functools import wraps
from nimbus.libs.bacula import ReloadManager





def connect_on(function, model, signal):

    @wraps(function)
    def function_wrapper(sender, instance, signal, *args, **kwargs):
        value = function(instance)
        reload_manager = ReloadManager()
        reload_manager.add_reload_request()
        return value

    signal.connect(function_wrapper, sender=model, weak=False)



