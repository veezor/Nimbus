#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
import difflib


from django.test import TestCase
from django.conf import settings

from nimbus.config import models, admin, commands


EXPECTED_BCONSOLE_FILE="""\
Director {
    Address = 8.8.8.8
    Name = director_name_test
    Password = "Bazinga!"
    DIRPort = 9101
}
"""

EXPECTED_DIRECTOR_FILE="""\
Director {
	Name = director_name_test
	Password = "Bazinga!"
	Maximum Concurrent Jobs = 99
	WorkingDirectory = "/var/bacula/working"
	DIRport = 9101
	Messages = Standard
	PidDirectory = "/var/run"
	QueryFile = "/etc/bacula/query.sql"
	FD Connect Timeout = 30 seconds
	SD Connect Timeout = 30 seconds
}

Catalog {
    DB Address = 127.0.0.1
	dbuser = 
	dbpassword = ""
	Name = MyCatalog
    dbname = ":memory:"
}

Messages {
	console = all, !skipped, !saved
	Name = Standard
	append = "/var/bacula/working/log" = all, !skipped
    mailcommand = "/var/www/nimbus --email-report %i" 
    operatorcommand = "/var/www/nimbus --email-report %i" 
    mail = nimbus@veezor.com = all, !skipped
    operator = nimbus@veezor.com = mount
}



@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/computers/* ; do echo @${f} ; done'"
@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/filesets/* ; do echo @${f} ; done'"
@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/jobs/* ; do echo @${f} ; done'"
@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/pools/* ; do echo @${f} ; done'"
@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/schedules/* ; do echo @${f} ; done'"
@|"sh -c 'for f in %(ROOT)s/var/nimbus/custom/storages/* ; do echo @${f} ; done'"
"""

class ConfigModelTest(TestCase):

    def setUp(self):
        self.maxDiff = None
    
    def test_create_bacula_name(self):
        config = models.Config(name="test")
        config.save()
        self.assertEqual(config.director_name, config.uuid.uuid_hex)

    def test_not_create_bacula_name(self):
        config = models.Config(name="test", director_name="director_name")
        config.save()
        self.assertEqual(config.director_name, "director_name")


    def test_update_director_file(self):
        template = EXPECTED_DIRECTOR_FILE
        config =  models.Config(name="test",
                                director_name="director_name_test",
                                director_address="8.8.8.8",
                                director_password="Bazinga!")
        config.save()

        template = template.replace("%(ROOT)s", settings.ROOT_PATH)


        with file(settings.BACULADIR_CONF) as f_obj:
            content =  f_obj.read()
            self.assertMultiLineEqual(content, template)


    def test_update_console_file(self):
        config =  models.Config(name="test",
                                director_name="director_name_test",
                                director_address="8.8.8.8",
                                director_password="Bazinga!")
        config.save()

        with file(settings.BCONSOLE_CONF) as f_obj:
            content =  f_obj.read()
            self.assertMultiLineEqual(content, EXPECTED_BCONSOLE_FILE)

class ConfigAdminRegistry(TestCase):

    def test_config(self):
        self.assertTrue( models.Config in admin.admin.site._registry)


class ConfigCommandsTest(TestCase):

    def test_create_config_dirs(self):
        with mock.patch("os.makedirs") as makedirs:
            commands.create_conf_dirs()
            expected_dirs = [ "/var/nimbus/custom/certificates",
                              "/var/nimbus/custom/computers",
                              "/var/nimbus/custom/config",
                              "/var/nimbus/custom/devices",
                              "/var/nimbus/custom/filesets",
                              "/var/nimbus/custom/jobs",
                              "/var/nimbus/custom/pools",
                              "/var/nimbus/custom/schedules",
                              "/var/nimbus/custom/storages",
                              "/etc/nimbus" ]

            for e_dir in expected_dirs:
                dir_name = settings.ROOT_PATH + e_dir
                makedirs.assert_any_call(dir_name)




class CreateDbCommandTest(TestCase):

    def setUp(self):
        self.patch_call_command =\
                mock.patch("nimbus.config.commands.call_command")
        self._apply_call_command_patch()

        self.patch_register =\
        mock.patch("nimbus.config.commands.register_administrative_nimbus_models")
        self.register = self.patch_register.start()

        self.patch_reload =\
                mock.patch("nimbus.config.commands.call_reload_baculadir")
        self.reload = self.patch_reload.start()

        self.patch_unlock =\
        mock.patch("nimbus.config.commands.force_unlock_bacula_and_start")
        self.unlock = self.patch_unlock.start()


        self.activate = commands.Computer.activate
        commands.Computer.activate = mock.Mock()

        self.computer_password = "isO1gYFdWfoZcpmj9YWo" 
        self.director_password = "tKuMvzdjmL6J4weOUf95" 
        self.storage_password = "rxRfVzGV9g78uTymo1sc"

    def _apply_call_command_patch(self):
        self.call_command = self.patch_call_command.start()

        def side_effect(*args, **kwargs):
            self.patch_call_command.stop()
        self.call_command.side_effect=side_effect




    def test_create_db(self):
        commands.create_database()
        self.call_command.assert_called_with('syncdb', 
                                             verbosity=0,
                                             interactive=False)
        self.assertEqual(commands.User.objects.count(), 1)

        computer = commands.Computer.objects.get(id=1)
        self.assertNotEqual(computer.password, self.computer_password)
        commands.Computer.activate.assert_called_with()


        storage = commands.Storage.objects.get(id=1)
        self.assertNotEqual(storage.password, self.storage_password)


        config = commands.Config.get_instance()
        self.assertNotEqual(config.director_password, self.director_password)

        self.register.assert_called_with()
        self.reload.assert_called_with()
        self.assertFalse(self.unlock.called)

        self._apply_call_command_patch()
        commands.create_database()
        self.unlock.assert_called_with()
        



    def tearDown(self):
        #self.patch_call_command.stop()
        self.patch_reload.stop()
        self.patch_register.stop()
        self.patch_unlock.stop()
        commands.Computer.activate = self.activate
