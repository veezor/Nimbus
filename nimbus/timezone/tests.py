#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import time
import subprocess

from django.conf import settings
from django.test import TestCase
from django.core.exceptions import ValidationError

from nimbus.timezone import models
from nimbus.shared.middlewares import ThreadPool



class TimezoneTest(TestCase):


    def test_default_servers(self):
        with mock.patch("subprocess.check_call") as check_call:
            servers = ["a.ntp.br",
                       "b.ntp.br",
                       "c.ntp.br",
                       "d.ntp.br",
                       "pool.ntp.br",
                       "pool.ntp.org"]
            for server in servers:
                conf = models.Timezone(ntp_server=server,
                                       country="Brazil",
                                       area="America/Recife")
                conf.clean()
                self.assertFalse(check_call.called)


    def test_clean_validation(self):
        with mock.patch("subprocess.check_call") as check_call:
            conf = models.Timezone(ntp_server="my.ntpserver.com.br",
                                   country="Brazil",
                                   area="America/Recife")
            conf.clean()
            check_call.assert_called_with(['/usr/sbin/ntpdate', 
                                           '-q', 
                                           'my.ntpserver.com.br'], 
                                           stderr=subprocess.PIPE, 
                                           stdout=subprocess.PIPE)

    def test_clean_validation_error(self):
        with mock.patch("subprocess.check_call") as check_call:
            check_call.side_effect = subprocess.CalledProcessError(0, "")
            conf = models.Timezone(ntp_server="my.ntpserver.com.br",
                                   country="Brazil",
                                   area="America/Recife")
            self.assertRaises(ValidationError, conf.clean)
            check_call.assert_called_with(['/usr/sbin/ntpdate', 
                                           '-q', 
                                           'my.ntpserver.com.br'], 
                                           stderr=subprocess.PIPE, 
                                           stdout=subprocess.PIPE)



    def test_update_system_timezone(self):
        conf = models.Timezone(ntp_server="my.ntpserver.com.br",
                               country="Brazil",
                               area="America/Recife")

        with mock.patch("nimbus.timezone.models.ServerProxy") as ServerProxy:
            with mock.patch("time.tzset") as tzset:
                threadp = ThreadPool()
                conf.save()
                time.sleep(2.0) # wait thread start
                ServerProxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
                proxy = ServerProxy.return_value
                proxy.change_timezone.assert_called_with("America/Recife")
                tzset.assert_called_with()
                threadp.instance.stop()
                ThreadPool.instance = None



    def test_update_cron_file(self):
        conf = models.Timezone(ntp_server="my.ntpserver.com.br",
                               country="Brazil",
                               area="America/Recife")

        with mock.patch("nimbus.timezone.models.ServerProxy") as ServerProxy:
            with mock.patch("time.tzset") as tzset:
                threadp = ThreadPool()
                conf.save()
                time.sleep(2.0) # wait thread start
                ServerProxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
                proxy = ServerProxy.return_value
                proxy.generate_ntpdate_file_on_cron.\
                        assert_called_with("my.ntpserver.com.br")
                threadp.instance.stop()
                ThreadPool.instance = None

    def test_update_system_timezone(self):
        conf = models.Timezone(ntp_server="my.ntpserver.com.br",
                               country="Brazil",
                               area="America/Recife")

        with mock.patch("nimbus.timezone.models.ServerProxy") as ServerProxy:
            with mock.patch("time.tzset") as tzset:
                threadp = ThreadPool()
                conf.save()
                time.sleep(2.0) # wait thread start
                ServerProxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
                proxy = ServerProxy.return_value
                proxy.change_timezone.assert_called_with("America/Recife")
                tzset.assert_called_with()
                threadp.instance.stop()
                ThreadPool.instance = None

