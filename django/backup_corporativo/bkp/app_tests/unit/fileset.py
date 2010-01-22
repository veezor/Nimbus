#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from django.core import management

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Procedure, FileSet
from backup_corporativo.bkp.tests import NimbusUnitTest

class FilesetUnitTest(NimbusUnitTest):
    
    def test(self):
        management.call_command('loaddata', 'fileset.json', verbosity=0)
        proc = Procedure.objects.get(pk=1)
        fset = FileSet(path='/var/', procedure=proc)
        fset.save()
        # Armazenando a entrada de fileset
        re_path = re.compile('''\t\tFile = "%s"\n''' % fset.path)
        # Removendo fileset
        fset.delete()
        # Buscando pela entrada de fileset
        fname = proc.fileset_bacula_name()
        fpath = utils.absolute_file_path(fname, 'filesets')
        self.files_to_remove.append(fpath)
        f = open(fpath, 'r')
        for line in f:
            # Entrada de fileset nao deve existir
            self.assertFalse(re.match(re_path, line))