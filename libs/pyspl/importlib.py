#!/usr/bin/env python
# -*- coding: UTF-8 -*-


def split_module_name(name):
    lastdotindex = name.rindex('.')
    items = name[:lastdotindex]
    item = name[lastdotindex + 1:]
    return items.strip(), item.strip()


def _import(module_name):
    if "." in module_name:
        package, attr = split_module_name(module_name)
        module = __import__(package, fromlist=[attr])
        if module.__name__ == module_name:
            return module
        else:
            return getattr( module, attr )
    else:
        return __import__(module_name)


def get_callback(callback):
    if isinstance( callback, basestring) :
        return _import(callback)
    return callback



def get_asset_from_name( name ):
    try:
        asset = _import(name)
        return asset
    except ImportError, e:
        clsname, methname = split_module_name( name )
        cls = _import( clsname )
        return getattr( cls, methname )




