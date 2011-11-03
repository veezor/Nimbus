#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getpass

from django.contrib.auth.models import User
from nimbus.libs.commands import command


@command('--change-password')
def change_password():

    while True:
        password = getpass.getpass("new password: ")
        confirm_password = getpass.getpass("confirm password: ")

        if password != confirm_password:
            print "password does not match"
            print
        else:
            user = User.objects.get(id=1)
            user.set_password(password)
            user.save()
            print "password changed"
            break


