#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import mock
import unittest
import datetime

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from django.conf import settings

import pybacula
import pybacula.backends
from nimbus.libs import bacula
from nimbus.shared.middlewares import LogSetup

LogSetup()

class BaculaTest(unittest.TestCase):


    def setUp(self):
        self.mock = mock.Mock(spec=pybacula.backends.IConsole)
        pybacula.backends._active_backend = self.mock
        self.bacula = bacula.Bacula()
        self.backend = self.bacula.cmd.backend


    def tearDown(self):
        pass


    def test_delete_pool(self):
        self.bacula.delete_pool("pool_name")
        self.backend.execute_command.assert_called_with( 'delete pool="pool_name" \nyes' )

    def test_truncate_volumes(self):
        self.bacula.truncate_volumes("pool_name")
        self.backend.execute_command.assert_called_with( 'purge volume action="truncate" pool="pool_name"' )

    def test_purge_volumes(self):
        self.bacula.purge_volumes(["testa", "testb"], "pool_name")
        self.backend.execute_command.assert_called_with( 'purge volume="testa" volume="testb" pool="pool_name"' )


    def test_cancel_job(self):
        self.bacula.cancel_job(job_id=1)
        self.backend.execute_command.assert_called_with('cancel jobid="1"')

    def test_cancel_procedure(self):
        procedure = mock.Mock()
        procedure.bacula_name = "test_name"
        procedure.jobs_id_to_cancel = [1,2,3]
        self.bacula.cancel_procedure(procedure)
        self.backend.execute_command.assert_any_call('cancel job="test_name"')
        self.backend.execute_command.assert_any_call('cancel jobid="1"')
        self.backend.execute_command.assert_any_call('cancel jobid="2"')
        self.backend.execute_command.assert_any_call('cancel jobid="3"')


    def test_run_backup(self):
        self.bacula.run_backup("job_name","client_name")
        self.backend.execute_command.assert_called_with('run client="client_name" job="job_name" yes')


    def test_restore(self):
        with mock.patch('nimbus.bacula.models.File.objects') as mock_objs:
            with mock.patch('__builtin__.file') as mock_file:
                with mock.patch('tempfile.mktemp') as mock_temp:
                    mock_temp.return_value = "filename"
                    path3 = mock.Mock()
                    path3.fullname = "/path"
                    mock_objs.select_related.return_value.filter.return_value = [ path3 ]
                    self.bacula.run_restore("client_name", "jobid", "where_client_name", ["file1", "file2/"])
        self.backend.execute_command.assert_called_with('restore client="client_name"\
 file="<filename" restoreclient="client_name"\
 select all done yes where="where_client_name"\
 jobid="jobid"')
        mock_file.assert_called_with("filename", "w")
        m_file = mock_file.return_value.__enter__.return_value
        m_file.write.assert_any_call("file1\n")
        m_file.write.assert_any_call("file2/\n")
        m_file.write.assert_any_call("/path\n")



    def test_get_items_from_bconsole_output(self):
        output = """
        1\ta
        2\tc
        3\tb
        """
        value = self.bacula._get_items_from_bconsole_output(output)
        self.assertEqual(value, ["a","b","c"])


    def test_list_files(self):

        with mock.patch("nimbus.libs.bacula.Bacula._get_items_from_bconsole_output") as mock_get:
            mock_get.side_effect= [ ["a/", "b/"], ["c"] ]
            value = self.bacula.list_files("jobid", "/path/")
            self.backend.execute_command.assert_any_call('.bvfs_update')
            self.backend.execute_command.assert_any_call('.bvfs_lsdir jobid="jobid" path="/path/"')
            self.backend.execute_command.assert_any_call('.bvfs_lsfiles jobid="jobid" path="/path/"')
            self.assertEqual(value, [u"/path/a/", u"/path/b/", u"/path/c"])



    def test_reload(self):
        with mock.patch("nimbus.libs.bacula.configcheck") as mock_config:
            self.backend.execute_command.return_value = True
            value = self.bacula.reload()
            mock_config.check_baculadir.assert_called_with(settings.BACULADIR_CONF)
            mock_config.check_bconsole.assert_called_with(settings.BCONSOLE_CONF)
            self.backend.execute_command.assert_called_with('reload')
            self.assertTrue(value)




    def test_bacula_lock_object(self):
        with mock.patch('nimbus.libs.bacula.lock_and_stop_bacula') as mock_lock:
            with mock.patch('nimbus.libs.bacula.unlock_bacula_and_start') as mock_unlock:
                with bacula.BaculaLock() as lock:
                    pass

        mock_lock.assert_called_with()
        mock_unlock.assert_called_with()


    def test_force_bacula_restart(self):
        with mock.patch('xmlrpclib.ServerProxy') as mock_proxy:
            with mock.patch('nimbus.libs.bacula.bacula_is_locked') as mock_is_locked:
                mock_is_locked.return_value = False
                bacula._force_baculadir_restart()


        mock_proxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
        mock_proxy.return_value.director_restart.assert_called_with()



    def test_call_reload_bacula_dir(self):
        with mock.patch('nimbus.libs.bacula.Bacula') as mock_bacula:
            with mock.patch('nimbus.libs.bacula._force_baculadir_restart') as mock_restart:
                def side_effect():
                    raise bacula.BConsoleInitError()
                mock_bacula.return_value.reload.side_effect = side_effect
                bacula.call_reload_baculadir()


        mock_restart.assert_called_with()
        mock_bacula.return_value.reload.assert_called_with()


    def test_lock_and_stop_bacula(self):
        with mock.patch('nimbus.libs.bacula.bacula_is_locked') as mock_locked:
            with mock.patch('xmlrpclib.ServerProxy') as mock_proxy:
                with mock.patch('__builtin__.file') as mock_file:
                    mock_locked.return_value = False
                    bacula.lock_and_stop_bacula()


        mock_proxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
        mock_file.assert_called_with(settings.BACULA_LOCK_FILE, "w")
        mock_proxy.return_value.director_stop.assert_called_with()


    def test_force_unlock_bacula_and_start(self):
        with mock.patch('os.remove') as mock_remove:
            with mock.patch('xmlrpclib.ServerProxy') as mock_proxy:
                bacula.force_unlock_bacula_and_start()


        mock_proxy.assert_called_with(settings.NIMBUS_MANAGER_URL)
        mock_remove.assert_called_with(settings.BACULA_LOCK_FILE)
        mock_proxy.return_value.director_start.assert_called_with()



    def test_unlock_bacula_and_start(self):
        with mock.patch('nimbus.libs.bacula.bacula_is_locked') as mock_locked:
            with mock.patch('nimbus.libs.bacula.force_unlock_bacula_and_start') as mock_start:
                mock_locked.return_value = True
                bacula.unlock_bacula_and_start()


        mock_locked.assert_called_with()
        mock_start.assert_called_with()


    def test_bacula_is_locked(self):
        with mock.patch('os.path.exists') as mock_:
            mock_.return_value = True
            value = bacula.bacula_is_locked()
            self.assertTrue(value)
            mock_.assert_called_with(settings.BACULA_LOCK_FILE)




if __name__ == "__main__":
    unittest.main()

