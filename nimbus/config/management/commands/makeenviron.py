#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError

class Command(NoArgsCommand):                                                                                                                                
    help = "Generate and test nimbus directories."

    requires_model_validation = False

    def handle_noargs(self, **options):
        
        members = dir(settings)
        directories = [ member for member in members if member.endswith("_DIR") ]
        directories = [ getattr(settings, dr) for dr in directories ]
        directories.remove( settings.FILE_UPLOAD_TEMP_DIR ) 
        
        for d in directories:
            try:
                os.makedirs(d)
            except OSError, error:
                if (error.strerror == "FileExists" and\
                        not os.access(d, os.W_OK)) or\
                        error.strerror == "Permission denied":
                    raise CommandError("%s is not writable" % d)

        shutil.copy( settings.NIMBUS_UNDEPLOYED_LOG_CONF, 
                     settings.NIMBUS_ETC_DIR)
