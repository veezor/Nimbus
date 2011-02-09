#!/usr/bin/env python
# -*- coding: UTF-8 -*-



class Router(object):


    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'bacula':
            return 'bacula'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        if not hasattr(model, "_meta"):
            return 'default'

        if model._meta.app_label == 'bacula':
            return 'bacula'
        else:
            return 'default'


    def allow_relation(self, obj1, obj2, **hints):
        return True


    def allow_syncdb(self, db, model):
        if db ==  model._meta.app_label == "bacula":
            return True
        if model._meta.app_label == "bacula" and db != "bacula":
            return False
        if db == "default" and model._meta.app_label != "bacula":
            return True
        return None
