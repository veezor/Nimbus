#!/usr/bin/env python

import os, sys
sys.path.extend( ['/var/nimbus/deps/', '/var/nimbus/hg/libs', '/var/nimbus/hg/django' ] )

os.environ['DJANGO_SETTINGS_MODULE'] = 'backup_corporativo.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
