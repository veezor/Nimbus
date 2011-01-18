#!/usr/bin/env python
# -*- coding: UTF-8 -*-



class Router(object):


    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'relationshipcenter':
            return 'relationshipcenter'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'relationshipcenter':
            return 'relationshipcenter'
        else:
            return 'default'


    def allow_relation(self, obj1, obj2, **hints):
        return True


    def allow_syncdb(self, db, model):
        if db ==  model._meta.app_label == "relationshipcenter":
            return False
        if model._meta.app_label == "relationshipcenter" and db != "relationshipcenter":
            return False
        if db == "default" and model._meta.app_label != "relationshipcenter":
            return True
        return None
