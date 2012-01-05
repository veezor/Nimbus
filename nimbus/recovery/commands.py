#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.libs.commands import command
from nimbus.recovery import models



@command("--rewrite-nimbus-conf")
def rewrite_nimbus_conf():
    return models.rewrite_nimbus_conf_files()


@command("--recovery-nimbus")
def recovery_nimbus():
    return models.recovery_nimbus_from_offsite()

