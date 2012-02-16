#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import mock
import unittest
import systeminfo

class DiskInfoTest(unittest.TestCase):

    def setUp(self):
        self.patch = mock.patch("os.statvfs")
        self.mock = self.patch.start()
        self.vfs_info = mock.Mock()
        self.vfs_info.f_bsize = 100
        self.vfs_info.f_blocks = 100
        self.vfs_info.f_bfree = 50
        self.mock.return_value = self.vfs_info
        self.disk_info = systeminfo.DiskInfo("/")

    def tearDown(self):
        self.mock.stop()

    def test_used(self):
        self.assertEqual( self.disk_info.get_used(), 5000) # 100*100

    def test_get_data(self):
        self.assertEqual( self.disk_info.get_data(), (10000, 5000, 5000))

    def test_get_usage(self):
        self.assertEqual( self.disk_info.get_usage(), 50) # 50%


class CPUInfoTest(unittest.TestCase):

    def setUp(self):
        self.patch_file = mock.patch("__builtin__.file")
        self.mock_file = self.patch_file.start()
        self.readline_mock = self.mock_file.return_value.__enter__.return_value.readline
        self.readline_mock.return_value = "cpu  1 2 3 4 5 6 7 0 0"
        self.patch_sleep = mock.patch("time.sleep")
        self.mock_sleep = self.patch_sleep.start()
        def side_effect(*args):
            self.readline_mock.return_value = "cpu  10 20 30 40 50 60 70 0 0"
        self.mock_sleep.side_effect = side_effect
        self.cpu_info = systeminfo.CPUInfo()


    def test_data_diff(self):
        diff = self.cpu_info.get_data_diff(1)
        self.assertEqual(diff, [9, 18, 27, 36, 45, 54])

    def test_usage(self):
        usage = self.cpu_info.get_usage()
        #usage = (n1+n2/n1..+..n6*)100
        self.assertAlmostEqual( usage, 28.5714, places=4)

    def tearDown(self):
        self.mock_sleep.stop()
        self.mock_file.stop()

class MemoryInfoTest(unittest.TestCase):

    def setUp(self):
        self.patch = mock.patch("__builtin__.file")
        self.mock = self.patch.start()
        self.mock.return_value.__enter__.return_value.readlines.return_value = ["x 10000", #total
                                                                                "x  5000", #free
                                                                                "x  1000", #buffers
                                                                                "x  1000"] #cached
        self.disk_info = systeminfo.MemoryInfo()


    def test_get_data(self):
        self.assertEqual( self.disk_info.get_data(), [10000, 5000, 1000, 1000])

    def test_get_usage(self):
        self.assertEqual( self.disk_info.get_usage(), 30) # 50% 10000 - (5000 +1000 + 1000)


    def tearDown(self):
        self.mock.stop()

if __name__ == "__main__":
    unittest.main()



