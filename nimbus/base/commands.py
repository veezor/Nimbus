#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

from django.core.management import call_command
from django.utils.translation import ugettext as _

from nimbus.libs.commands import command
from nimbus.libs import migrations


@command("--shell")
def shell():
    _(u"""Start django's shell""")
    call_command('shell')


@command("--update-1.0-to-1.1")
def update_10_to_11():
    _(u"""Migrate from version 1.0 to 1.1""")
    try:
        migrations.update_10_to_11()
    except migrations.ComputerUpdateError:
        print _(u"Error: all clients must be active on the network")
        sys.exit(1)


