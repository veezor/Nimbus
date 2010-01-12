#!/usr/bin/env python

import os, sys
sys.path.extend( [  "/var/nimbus/deps/",
                    "/var/lib/python-support/python2.5/", 
                    "/usr/lib/python2.5/",
                    "/usr/lib/python2.5i/site-packages/"])

os.environ['DJANGO_SETTINGS_MODULE'] = 'backup_corporativo.settings'

if len(sys.argv) == 2  and sys.argv[1] == "--test":
    from django.core.management import call_command
    call_command("test")
else:
    from django.core.servers.fastcgi import runfastcgi
    runfastcgi(method="threaded", daemonize="false")
