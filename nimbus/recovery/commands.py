#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.libs.commands import command
from nimbus.recovery import models





@command("--rewrite-nimbus-conf")
def rewrite_nimbus_conf():
    return models.rewrite_nimbus_conf_files()

