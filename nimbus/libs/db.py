#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models, transaction

class Session(object):

    def __init__(self, rollback_on_exception=True, 
                       commit_on_exit = True, db=None):

        self.models = set()
        self.rollback_on_exception = rollback_on_exception
        self.db = db
        self.commit_on_exit = commit_on_exit

    def add(self, model):
        if not isinstance(model, models.Model):
            raise TypeError("models.Model is required")
        self.models.add(model)

    def remove(self, model):
        if not isinstance(model, models.Model):
            raise TypeError("models.Model is required")
        return self.models.remove(model)


    def __len__(self):
        return len(self.models)

    def __iter__(self):
        return iter(self.models)

    def __contains__(self, model):
        return model in self.models

    def clear(self):
        self.models.clear()

    def as_list(self):
        return list(self.models)

    def commit(self):
        transaction.commit()
        self.commit_on_exit = False

    def rollback(self):

        for model in self.models:
            model.delete()

        transaction.rollback()
        self.commit_on_exit = False

    def open(self):
        transaction.enter_transaction_management(using=self.db)
        transaction.managed(True, using=self.db)

    def close(self):
        transaction.leave_transaction_management(using=self.db)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_type and self.rollback_on_exception:
            self.rollback()

        if self.commit_on_exit:
            self.commit()

        self.close()





