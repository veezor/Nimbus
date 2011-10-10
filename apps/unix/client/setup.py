#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
from distutils.core import setup


START_STOP_DAEMON = "/sbin/start-stop-daemon"
INITD_FILE = "etc/init.d/nimbusclient"
INITD_FILE_RH = "etc/init.d/nimbusclient.rh"
INITD_BAK_FILE = INITD_FILE + ".bak"


def is_rpm():
    return not os.path.exists(START_STOP_DAEMON)

def rename_initd_script():
    print os.listdir('etc/init.d')
    print os.listdir('.')
    if not os.path.exists(INITD_BAK_FILE):
        os.rename(INITD_FILE, INITD_BAK_FILE)
        os.rename(INITD_FILE_RH, INITD_FILE)

if is_rpm():
    rename_initd_script()


setup(name='Nimbus Client Service',
      version='1.0',
      description='Client for Nimbus Cloud Backup',
      author='Veezor',
      author_email='contact@veezor.com',
      license="GPL",
      url='www.nimbusbackup.com',
      data_files=[
          ('/etc/init.d', ['etc/init.d/nimbusclient']),
          ('/etc/nimbus', [])
      ],
      scripts=['usr/sbin/nimbusnotifier', 'usr/sbin/nimbusclientservice'],
     )
