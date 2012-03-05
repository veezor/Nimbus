#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
import string
import unittest

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from nimbus.shared import utils, signals
from nimbus.shared.middlewares import LogSetup

LogSetup()

class UtilsTest(unittest.TestCase):

    def test_filesize_format(self):
        units = ["bytes","Kb", "Mb", "Gb", "Tb"]
        for exp,unit in enumerate(units):
            value = utils.filesizeformat(1024 ** exp)
            self.assertEqual(value, "1.00 " + unit)

        for exp,unit in enumerate(["B","KB","MB","GB","TB"]):
            value = utils.filesizeformat(1024 ** exp, unit)
            self.assertEqual(value, "1.00 " + units[exp])

            value = utils.filesizeformat(1024 ** (exp+1), unit)
            self.assertEqual(value, "1024.00 " + units[exp])


    def test_referer(self):
        request = mock.Mock()
        request.META.get.return_value = "http://localhost/test1/test2"
        referer = utils.Referer(request)
        self.assertEqual(referer.local, "/test1/test2")

        request.META.get.return_value = "/test1/test2"
        referer = utils.Referer(request)
        self.assertEqual(referer.local, "/test1/test2")
        #self.assertEqual(referer.local, None)

        request.META.get.return_value = None
        referer = utils.Referer(request)
        self.assertEqual(referer.local, None)
        #self.assertEqual(referer.local, '')


    def test_ordered_dict_values_to_formated_float(self):
        data = {  1: 1.1, 2: 2.2, 3:3.3  }
        result = utils.ordered_dict_value_to_formatted_float(data)
        self.assertEqual(result, ["1.10", "2.20", "3.30"])

        data = {  1: 1.1, 2: 2.2, 3:"abc"  }
        self.assertRaises(TypeError, utils.ordered_dict_value_to_formatted_float, data)


    def test_bytes_to_mb(self):
        self.assertEqual( 1, utils.bytes_to_mb(1024**2) )
        self.assertEqual( 4, utils.bytes_to_mb(4*(1024**2)) )
        self.assertEqual( 1024, utils.bytes_to_mb(1024**3) )
        self.assertTrue( utils.bytes_to_mb(1023) < 1 )

    def test_random_password(self):
        password = utils.random_password(size=30)
        self.assertEqual(len(password), 30)

        def test(char):
            if char in string.letters or char in string.digits:
                return True
            return False
        self.assertTrue( all( c for c in password )  )


    def test_isdir(self):
        self.assertTrue( utils.isdir("/dir/") )
        self.assertFalse( utils.isdir("/notdir") )

    def test_remove_or_leave(self):
        with mock.patch("os.remove") as mock_remove:
            path = "/tmp/path"
            utils.remove_or_leave(path)
            mock_remove.assert_called_with(path)
            mock_remove.side_effect = OSError
            try:
                utils.remove_or_leave(path)
                raised=False
            except OSError:
                raised=True
            self.assertFalse(raised)


    def test_absolute_dir_path(self):
        with mock.patch("nimbus.shared.utils.settings") as mock_settings:
            mock_settings.NIMBUS_CUSTOM_DIR = "/test"
            path = utils.absolute_dir_path("abc")
            self.assertEqual(path, "/test/abc")


    def test_absolute_file_path(self):
        with mock.patch("nimbus.shared.utils.settings") as mock_settings:
            mock_settings.NIMBUS_CUSTOM_DIR = "/test"
            path = utils.absolute_file_path("file","dir")
            self.assertEqual(path, "/test/dir/file")

    def test_mount_path(self):
        with mock.patch("nimbus.shared.utils.settings") as mock_settings:
            mock_settings.NIMBUS_CUSTOM_DIR = "/test"
            basedir, filepath = utils.mount_path("filename", "relativedir")
            self.assertEqual(basedir, "/test/relativedir")
            self.assertEqual(filepath, "/test/relativedir/filename")


    def test_project_port(self):
        request = mock.Mock()
        request.META = {}
        request.META['SERVER_PORT'] = 80
        port = utils.project_port(request)
        self.assertEqual(port, ":80" )
        del request.META['SERVER_PORT']
        port = utils.project_port(request)
        self.assertEqual(port, '')



class SignalsTest(unittest.TestCase):

    def test_connect_on(self):
        signal = mock.Mock()
        callback = mock.Mock()
        callback.__name__ = "callback"
        model = mock.Mock()
        signals.connect_on(callback, model, signal)

        self.assertTrue(signal.connect.called)
        args, kwargs = signal.connect.call_args
        self.assertEqual(kwargs['weak'], False)
        self.assertEqual(kwargs['sender'], model)
        wrapped_callback = args[0]

        instance = mock.Mock()
        wrapped_callback(None, instance, None)
        callback.assert_called_with(instance)


if __name__ == "__main__":
    unittest.main()

