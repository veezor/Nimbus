#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

from django.core.management import call_command

from nimbus.libs.commands import command
from nimbus.libs import migrations


@command("--shell")
def shell():
    call_command('shell')


@command("--update-1.0-to-1.1")
def update_10_to_11():
    try:
        migrations.update_10_to_11()
    except migrations.ComputerUpdateError:
        print "Erro: todos os clientes devem estar ativos na rede"
        sys.exit(1)


