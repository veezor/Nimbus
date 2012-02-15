#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import bacula
import tempfile
import unittest
import operator
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



class CommandLineTestCase(unittest.TestCase):

    def setUp(self):
        self.patch = mock.patch('bacula.get_active_backend')
        self.mock = self.patch.start()
        self.backend = self.mock.return_value.return_value # look bacula.py:27

    def test_connection_error(self):
        self.backend.connect.side_effect = Exception("boom!")
        self.assertRaises(m_backends.BConsoleInitError, bacula.BaculaCommandLine)
        self.assertFalse( bacula.BaculaCommandLine.connected )

    def test_backend_initerror(self):
        self.mock.return_value.side_effect = m_backends.BConsoleInitError("bomm!")
        self.assertRaises(m_backends.BConsoleInitError, bacula.BaculaCommandLine)

    def test_connection(self):
        cmd_line = bacula.BaculaCommandLine()
        self.assertTrue( bacula.BaculaCommandLine.connected )
        bacula.BaculaCommandLine.connected = False

    def test_invalid_command(self):
        cmd_line = bacula.BaculaCommandLine()
        funct = operator.attrgetter('invalidcommand')
        self.assertRaises(bacula.CommandNotFound, funct, cmd_line)

    def test_dotted_command(self):
        cmd_line = bacula.BaculaCommandLine()
        cmd = cmd_line._bvfs_update
        self.assertEqual('.bvfs_update', cmd.get_content())

    def test_valid_command(self):
        cmd_line = bacula.BaculaCommandLine()
        try:
            cmd_line.reload
        except bacula.CommandNotFound:
            raise self.failureException, "valid command not found"

    def test_raw(self):
        cmd_line = bacula.BaculaCommandLine()
        value = cmd_line.raw('abcdef')
        args, kwargs = cmd_line.backend.execute_command.call_args
        self.assertEqual( 'abcdef', args[0] )

    def tearDown(self):
        self.patch.stop()




class CommandTest(unittest.TestCase):


    def setUp(self):
        self.cmd = bacula.Command("test")
        self.patch = mock.patch("bacula.BaculaCommandLine")
        self.mock = self.patch.start()
        self.mock.connected = True
        self.mock.backend.execute_command.return_value = "ok"

    def test_new(self):
        self.assertEqual(self.cmd.get_content(), "test")

    def test_raw(self):
        self.cmd.raw("test")
        self.assertEqual(self.cmd.get_content(), "test test")

    def test_dsl_attr(self):
        self.cmd.attrtest1.attrtest2.attrtest3
        self.assertEqual(self.cmd.get_content(), "test attrtest1 attrtest2 attrtest3")

    def test_dsl_getitem(self):
        self.cmd.attribute['value']
        self.assertEqual(self.cmd.get_content(), 'test attribute="value"')

    def test_run(self):
        result = self.cmd.run()
        self.assertEqual(result, "ok")
        r = self.mock.backend.execute_command.assert_called_with("test")
        self.assertTrue( r is None )
        self.assertEqual( self.cmd.get_content(), "test" )


    def test_call(self):
        result = self.cmd.run()
        self.assertEqual(result, "ok")
        r = self.mock.backend.execute_command.assert_called_with("test")
        self.assertTrue( r is None )
        self.assertEqual( self.cmd.get_content(), "test" )



if __name__ == "__main__":
    unittest.main()


