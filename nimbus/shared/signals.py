#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from functools import wraps


def connect_on(function, model, signal):
    "Simplify django signals callbacks"

    @wraps(function)
    def function_wrapper(sender, instance, signal, *args, **kwargs):
        return function(instance)

    signal.connect(function_wrapper, sender=model, weak=False)



