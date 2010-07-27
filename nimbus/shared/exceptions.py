#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class MyBaseException(Exception):

    def __str__(self):
        return self.__class__.__doc__

