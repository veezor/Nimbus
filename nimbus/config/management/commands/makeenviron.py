#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

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

        members = dir(settings)
        directories = [member for member in members if member.endswith("_DIR")]
        directories = [getattr(settings, dr) for dr in directories]
        directories.remove(settings.FILE_UPLOAD_TEMP_DIR)
        for d in directories:
            try:
                if prefix:
                    d = prefix + "/" + d
                print d
                os.makedirs(d)
            except OSError, error:
                if (error.strerror == "FileExists" and \
                        not os.access(d, os.W_OK)) or\
                        error.strerror == "Permission denied":
                    raise CommandError("%s is not writable" % d)

        if prefix:
            etc_dir = prefix +  '/' + settings.NIMBUS_ETC_DIR
        else:
            etc_dir = settings.NIMBUS_ETC_DIR

        shutil.copy(settings.NIMBUS_UNDEPLOYED_LOG_CONF,
                    etc_dir)
