#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import shutil
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from nimbus.config import commands

class Command(BaseCommand):
    args = "prefix"
    help = "Generate and test nimbus directories."
    requires_model_validation = False

    def handle(self, *args, **options):
        prefix = ""
        if len(args) == 0:
            pass
        elif len(args) == 1:
            prefix = args[0]
        else:
            raise CommandError("makeenviron requires just one argument")

        commands.create_conf_dirs(prefix)

        if prefix:
            etc_dir = prefix +  '/' + settings.NIMBUS_ETC_DIR
        else:
            etc_dir = settings.NIMBUS_ETC_DIR

        shutil.copy(settings.NIMBUS_UNDEPLOYED_LOG_CONF,
                    etc_dir)
