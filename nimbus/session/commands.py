#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import getpass

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from nimbus.libs.commands import command


@command('--change-password')
def change_password():
    _(u"""Change admin password""")

    while True:
        password = getpass.getpass(_("new password: "))
        confirm_password = getpass.getpass(_("confirm password: "))

        if password != confirm_password:
            print _("password does not match")
            print
        else:
            user = User.objects.get(id=1)
            user.set_password(password)
            user.save()
            print _("password changed")
            break


