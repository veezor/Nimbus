#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import tempfile
import unittest
import backends as m_backends
import configcheck


class ConfigCheckTestCase(unittest.TestCase):

    def test_check_exception_on_executable_error(self):
        filename = tempfile.mktemp()
        with mock.patch('subprocess.Popen') as popen_mock:
            popen_mock.return_value.returncode = 1
            self.assertRaises(configcheck.ConfigFileError,
                              configcheck._call_test_command,
                              "/bin/false", filename)


    def test_check_exception_on_executable_not_found(self):
        filename = tempfile.mktemp()
        self.assertRaises(configcheck.ConfigFileError,
                          configcheck._call_test_command,
                          "/bin/notfounexecutable", # ;)
                          filename)


    def test_command(self):
        filename = tempfile.mktemp()
        with mock.patch('subprocess.Popen') as popen_mock:
            popen_mock.return_value.returncode = 0
            configcheck.check_baculadir(filename)

            args = popen_mock.call_args[0]
            cmd = args[0]
            self.assertEqual(cmd, [configcheck.BACULA_DIR,"-t","-c",filename])




class BackendsTest(unittest.TestCase):


    def test_get_availabe_backends(self):
        backends = m_backends.get_available_backends()
        self.assertTrue( m_backends.MockConsole in backends )
        self.assertTrue( m_backends.SubprocessConsole in backends )


    def test_new_backends(self):

        class TestBackend(m_backends.IConsole):
            pass


        backends = m_backends.get_available_backends()
        self.assertTrue( TestBackend in backends )


    def test_install_new_backend(self):
        current_backend = m_backends.get_active_backend()

        class TestBackend(m_backends.IConsole):
            pass

        m_backends.install_backend(TestBackend)
        backend = m_backends.get_active_backend()

        self.assertEquals(TestBackend, backend)
        self.assertNotEquals(current_backend, backend)


    def test_install_backend_method(self):

        current_backend = m_backends.get_active_backend()
        class Test(m_backends.IConsole):
            pass

        Test.install()
        backend = m_backends.get_active_backend()

        self.assertEquals(Test, backend)
        self.assertNotEquals(current_backend, backend)


    def test_install_test_backend(self):
        current_backend = m_backends.get_active_backend()

        m_backends.install_test_backend()

        backend = m_backends.get_active_backend()

        self.assertEquals(m_backends.MockConsole, backend)
        self.assertNotEquals(current_backend, backend)


    def test_not_install_backend(self):
        current_backend = m_backends.get_active_backend()

        m_backends.install_backend(None)
        backend = m_backends.get_active_backend()

        self.assertEquals(current_backend, backend)




class SubprocessBackendTestCase(unittest.TestCase):

    def test_config_file_not_found(self):
        backend = m_backends.SubprocessConsole()
        self.assertRaises(m_backends.BConsoleInitError, backend.execute_command, "cmd")


    def test_bconsole_executable(self):
        with mock.patch('backends.BCONSOLE_EXECUTABLE', "notisarealexecutable") as bconsole_mock: # ;)
            backend = m_backends.SubprocessConsole()
            self.assertRaises(m_backends.BConsoleInitError, backend.execute_command, "cmd")





class SubprocessTestCase(unittest.TestCase): # mock subprocess

    def setUp(self):
        self.patch = mock.patch('backends.Popen')
        self.mock = self.patch.start()
        self.mock.return_value.communicate.return_value = ("stdout", "stderr")
        self.backend = m_backends.SubprocessConsole()

    def tearDown(self):
        self.mock.stop()

    def test_execute_error(self):
        self.mock.return_value.returncode = 2 # != 0
        self.assertRaises(m_backends.BConsoleInitError,self.backend.execute_command, "cmd")

    def test_output(self):
        self.mock.return_value.returncode = 0
        result = self.backend.execute_command("hello")
        self.assertEquals(result, "stdout")

    def test_input(self):
        cmd = "helo"
        self.mock.return_value.returncode = 0
        self.backend.execute_command(cmd)

        args = self.mock.return_value.communicate.call_args[0]
        called_cmd = args[0]
        self.assertEquals( cmd, called_cmd )






if __name__ == "__main__":
    unittest.main()


