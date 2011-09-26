#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Mock(object):

    def __getattr__(self, attr):
        return self

    def __call__(self, *args, **kwargs):
        return self
