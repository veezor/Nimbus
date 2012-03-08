#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class MyBaseException(Exception):

    def __init__(self, *args, **kwargs):
        super(MyBaseException, self).__init__(*args, **kwargs)
        self.message = self.__class__.__doc__

    def __str__(self):
        return self.__class__.__doc__

