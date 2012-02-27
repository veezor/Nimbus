#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import tempfile
import unittest

os.environ['DJANGO_SETTINGS_MODULE'] = 'nimbus.settings'

from nimbus.libs import template
from nimbus.shared.middlewares import LogSetup

LogSetup()

class TemplatesTest(unittest.TestCase):

    def test_render_to_string(self):
        content = template.render_to_string("test_template", var="value")
        self.assertEqual(content, "Test value\n")

    def test_render_to_file(self):
        filename = tempfile.mktemp()
        template.render_to_file(filename, "test_template", var="other_value")
        with file(filename) as f:
            content = f.read()
        os.unlink(filename)
        self.assertEqual(content, "Test other_value\n")




if __name__ == "__main__":
    unittest.main()

