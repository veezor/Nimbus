#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.shared.exceptions import MyBaseException



class UUIDViolation(MyBaseException):
    """Model instance has uuid_hex value before save method"""


class UUIDChanged(MyBaseException):
    """ Model change your uuid primary key """
