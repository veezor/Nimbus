#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import mock
import string
import unittest

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'


from django.db import models
from django.conf import settings
import django.forms as dforms

from nimbus.shared.middlewares import LogSetup

from nimbus.shared import (utils,
                           signals,
                           middlewares,
                           fields,
                           forms,
                           views)

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


class MiddlewaresTest(unittest.TestCase):


    def test_logsetup(self):
        with mock.patch('logging.config.fileConfig') as mock_config:
            middlewares.LogSetup()
            mock_config.assert_called_with(settings.LOGGING_CONF)


    def test_threadpool(self):
        with mock.patch('nimbus.shared.middlewares.BJThreadPool') as mock_threadpool:
            self.assertEqual(middlewares.ThreadPool.instance, None)
            self.assertEqual(middlewares.ThreadPool.get_instance(), None)
            middlewares.ThreadPool()
            self.assertEqual(middlewares.ThreadPool.instance, mock_threadpool.return_value)
            self.assertEqual(middlewares.ThreadPool.get_instance(), mock_threadpool.return_value)
            mock_threadpool.assert_called_with()


    def test_ajax_debug(self):
        with mock.patch('nimbus.shared.middlewares.traceback') as mock_traceback:
            with mock.patch('nimbus.shared.middlewares.logging') as mock_logging:
                middlewares.AjaxDebug().process_exception(request=None, exception=None)
                mock_traceback.print_exc.assert_called_with(file=sys.stderr)
                mock_logging.getLogger.assert_called_with('nimbus.shared.middlewares')
                self.assertTrue( mock_logging.getLogger.return_value.exception.called )




class FieldsTest(unittest.TestCase):

    def assertNotRaises(self, exception, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
            raised = False
        except exception:
            raised = True
        self.assertFalse(raised)

    def test_check_domain(self):
        self.assertRaises(fields.ValidationError, fields.check_domain, "abc")
        self.assertNotRaises(fields.ValidationError, fields.check_domain, "a.b.com")
        self.assertNotRaises(fields.ValidationError, fields.check_domain, "localhost")
        self.assertNotRaises(fields.ValidationError, fields.check_domain, "a.b.com:80")
        self.assertNotRaises(fields.ValidationError, fields.check_domain, "192.168.6.1")


    def test_check_model_name(self):
        self.assertNotRaises(fields.ValidationError, fields.check_model_name, "a b c")
        self.assertRaises(fields.ValidationError, fields.check_model_name, "1") #digits
        self.assertRaises(fields.ValidationError, fields.check_model_name, "abc") # len(str) < 3
        self.assertNotRaises(fields.ValidationError, fields.check_model_name, "abcd") # len(str) >= 4
        self.assertRaises(fields.ValidationError, fields.check_model_name, "abçd") # accentuation


    def test_name_is_valid(self):
        self.assertTrue(fields.name_is_valid("a b c"))
        self.assertFalse(fields.name_is_valid("1")) #digits
        self.assertFalse(fields.name_is_valid("abc"))# len(str) < 3
        self.assertTrue(fields.name_is_valid("abcd")) # len(str) >= 4
        self.assertFalse(fields.name_is_valid("abçd")) # accentuation


    def test_form_path(self):
        form = fields.FormPathField()
        self.assertRaises(fields.ValidationError, form.clean, "a b c")
        self.assertRaises(fields.ValidationError, form.clean, "abcd")
        self.assertNotRaises(fields.ValidationError, form.clean, "/abcd")
        self.assertRaises(fields.ValidationError, form.clean, "\abcd")
        self.assertNotRaises(fields.ValidationError, form.clean, "/abcd/")
        self.assertNotRaises(fields.ValidationError, form.clean, "/abcd/edf/abc")
        self.assertRaises(fields.ValidationError, form.clean, "\abcd\edf\abc")
        self.assertRaises(fields.ValidationError, form.clean, "C:")
        self.assertNotRaises(fields.ValidationError, form.clean, "C:/")
        self.assertNotRaises(fields.ValidationError, form.clean, "C:/abc")
        self.assertNotRaises(fields.ValidationError, form.clean, "C:/abc/def/ghi")


    def test_model_path(self):
        path_field = fields.ModelPathField()
        form_field = path_field.formfield()
        self.assertTrue(isinstance(form_field, fields.FormPathField))


    def test_char_form_field(self):
        widget = mock.Mock()

        def get_class_attr(max_length):
            char_form_field = fields.CharFormField(max_length=max_length)
            return char_form_field.widget_attrs(widget)['class']

        self.assertEqual(get_class_attr(30), 'text small')
        self.assertEqual(get_class_attr(50), 'text medium')
        self.assertEqual(get_class_attr(270), 'text big')


    def test_ip_address_field(self):
        widget = mock.Mock()

        ip_form_field = fields.IPAddressField()
        class_attr = ip_form_field.widget_attrs(widget)['class']

        self.assertEqual(class_attr, 'text small')




class ViewsTest(unittest.TestCase):

    def test_render_to_response(self):
        with mock.patch('nimbus.shared.views._render_to_response') as mock_render:
            with mock.patch('nimbus.shared.views.RequestContext') as mock_context:
                request = mock.Mock()
                template = "test_template"
                dictionary = {}
                views.render_to_response(request, template, dictionary)
                mock_context.assert_called_with(request)
                mock_render.assert_called_with(template, dictionary,
                                               context_instance=mock_context.return_value)




class EditSingletonModelTest(unittest.TestCase):

    def setUp(self):
        self.patch_update = mock.patch('nimbus.shared.views.update_object')
        self.update_object = self.patch_update.start()
        self.patch_create = mock.patch('nimbus.shared.views.create_object')
        self.create_object = self.patch_create.start()
        self.patch_reload = mock.patch('nimbus.shared.views.call_reload_baculadir')
        self.call_reload_baculadir = self.patch_reload.start()
        self.patch_reverse = mock.patch('nimbus.shared.views.reverse')
        self.reverse = self.patch_reverse.start()
        self.patch_form = mock.patch('nimbus.shared.forms.form')
        self.form = self.patch_form.start()

        self.request = mock.Mock()


    def _default_call(self,**kargs):
        views.edit_singleton_model(self.request,
                                   "test_template",
                                   redirect_to="nimbus.base.views.home",
                                   **kargs)

    def test_reverse(self):
        self._default_call()
        self.reverse.assert_called_with("nimbus.base.views.home")
        self.reverse.reset_mock()
        views.edit_singleton_model(self.request,
                                   "test_template",
                                   redirect_to="/")
        self.assertFalse(self.reverse.called)


    def test_create(self):
        self.update_object.side_effect = views.Http404

        self._default_call()
        self.assertTrue(self.create_object.called)


    def test_create_not_called(self):
        self._default_call()
        self.assertFalse(self.create_object.called)


    def test_reload(self):
        self.request.method = "POST"
        self._default_call(reload_bacula=False)
        self.assertFalse(self.call_reload_baculadir.called)
        self._default_call(reload_bacula=True)
        self.call_reload_baculadir.assert_called_with()

        self.call_reload_baculadir.reset_mock()

        self.request.method = "GET"
        self._default_call(reload_bacula=True)
        self.assertFalse(self.call_reload_baculadir.called)


    def test_update_object_call(self):
        self._default_call()
        self.update_object.assert_called_with(self.request,
                                              object_id=1,
                                              model=None,
                                              form_class=None,
                                              template_name="test_template",
                                              post_save_redirect=self.reverse.return_value,
                                              extra_context=None)

    def test_create_call(self):
        self.update_object.side_effect = views.Http404
        self._default_call()
        self.create_object.assert_called_with(self.request,
                                              model=None,
                                              form_class=None,
                                              template_name="test_template",
                                              post_save_redirect=self.reverse.return_value,
                                              extra_context=None)


    def test_form(self):
        self._default_call()
        self.assertFalse(self.form.called)
        model = mock.Mock()
        self._default_call(model=model)
        self.form.assert_called_with(model)


    def tearDown(self):
        self.patch_update.stop()
        self.patch_create.stop()
        self.patch_reload.stop()
        self.patch_reverse.stop()
        self.patch_form.stop()




class FormsTest(unittest.TestCase):


    def setUp(self):
        self.select_attrs = {"class":""}
        self.input_attrs = {"class":"text"}


    def _helper_test(self, field, widgettype, attrs):
        forms.make_custom_fields(field)
        self.assertTrue( field.formfield.called )
        args, kwargs = field.formfield.call_args
        widget = kwargs['widget']
        self.assertTrue(isinstance(widget, widgettype))
        self.assertEqual( widget.attrs, attrs )



    def generic_test(self, fieldtype, widgettype, attrs):
        field = mock.Mock(spec=fieldtype)
        field.choices = None
        self._helper_test(field, widgettype, attrs)

    def test_foreign_key_custom_field(self):
        self.generic_test(models.ForeignKey,
                          dforms.Select,
                          self.select_attrs)


    def test_choices(self):
        field = mock.Mock()
        field.choices = True
        self._helper_test(field,
                          dforms.Select,
                          self.select_attrs)



    def test_char_custom_field(self):
        self.generic_test(models.CharField,
                          dforms.TextInput,
                          self.input_attrs)


    def test_time_custom_field(self):
        self.generic_test(models.TimeField,
                          dforms.TextInput,
                          self.input_attrs)


    def test_positive_small_custom_field(self):
        self.generic_test(models.PositiveSmallIntegerField,
                          dforms.TextInput,
                          self.input_attrs)


    def test_many_to_many_custom_field(self):
        self.generic_test(models.ManyToManyField,
                          dforms.SelectMultiple,
                          self.select_attrs)


    def test_else(self):
        field = mock.Mock()
        field.choices = None
        forms.make_custom_fields(field)
        field.formfield.assert_called_with()


    def test_ipaddres(self):
        field = mock.Mock(spec=models.IPAddressField)
        field.choices = None
        forms.make_custom_fields(field)
        field.formfield.assert_called_with(form_class=fields.IPAddressField)


if __name__ == "__main__":
    unittest.main()



