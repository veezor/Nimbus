#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from django.test import TestCase
from django.conf import settings

from nimbus.filesets import models


class FileSetModelTest(TestCase):

    def setUp(self):
        self.fileset = models.FileSet(name="test")

    def test_unicode(self):
        self.assertEqual(unicode(self.fileset), u"test")

                    

class FilePathModelTest(TestCase):

    def setUp(self):
        self.fileset = models.FileSet(name="test")
        self.filepath = models.FilePath(path="/nimbus",
                                        fileset=self.fileset)

    def test_unicode(self):
        self.assertEqual(unicode(self.filepath), u"test - /nimbus") 



class WildCardModelTest(TestCase):

    def setUp(self):
        self.fileset = models.FileSet(name="test")
        self.fileset.save()
        self.wildcard = models.Wildcard(kind="I",
                                        expression="*.exe",
                                        fileset=self.fileset)
        self.wildcard.save()
        self.other_wildcard = models.Wildcard(kind="E",
                                   expression="*.avi",
                                   fileset=self.fileset)
        self.other_wildcard.save()


    def test_unicode(self):
        self.assertEqual(unicode(self.wildcard), u"Include: '*.exe'") 


        self.assertEqual(unicode(self.other_wildcard), u"Exclude: '*.avi'") 


    def test_fileset_includes(self):
        self.assertTrue( self.wildcard in self.fileset.includes)
        self.assertFalse( self.other_wildcard in self.fileset.includes )

    def test_fileset_excludes(self):
        self.assertFalse( self.wildcard in self.fileset.excludes )
        self.assertTrue( self.other_wildcard in self.fileset.excludes )

    def test_wildcard_conflicts(self):
        raise TODO

EXPECTED_BLANK_FILE="""\
## test
FileSet {
    Name = "%(bacula_name)s" 
    Include {
        Options{
            signature = "MD5" 
            compression = "GZIP"
            
        }
        
        
        
        
    }
}
"""

EXPECTED_FILEPATH_FILE="""\
## test
FileSet {
    Name = "%(bacula_name)s" 
    Include {
        Options{
            signature = "MD5" 
            compression = "GZIP"
            
        }
        
        
        
        File = "/nimbus"
        
    }
}
"""


EXPECTED_FILTERS_FILE="""\
## test
FileSet {
    Name = "%(bacula_name)s" 
    Include {
        Options{
            signature = "MD5" 
            compression = "GZIP"
            wildfile = "*.exe"
            
        }
        
        Options{
            wildfile = "*.avi"
            
            Exclude = yes
        }
        
        File = "/nimbus"
        
    }
}
"""
EXPECTED_FILTERS_FILE_2="""\
## test
FileSet {
    Name = "%(bacula_name)s" 
    Include {
        Options{
            signature = "MD5" 
            compression = "GZIP"
            wildfile = "*.exe"
            
        }
        
        
        Options{
            RegexFile = ".*"
            Exclude = yes
        }
        
        
        File = "/nimbus"
        
    }
}
"""


class SignalsTest(TestCase):

    def setUp(self):
        self.fileset = models.FileSet(name="test")
        self.fileset.save()
        name = self.fileset.bacula_name
        self.filename = os.path.join(settings.NIMBUS_FILESETS_DIR, name)

    def test_blank(self):
        with file(self.filename) as f_obj:
            content = f_obj.read()
            template = EXPECTED_BLANK_FILE %\
                    {"bacula_name" : self.fileset.bacula_name}
            self.assertMultiLineEqual(content, template)



    def test_filepath(self):
        filepath = models.FilePath(path=u"/nimbus",
                                   fileset=self.fileset)
        filepath.save()
        with file(self.filename) as f_obj:
            content = f_obj.read()
            template = EXPECTED_FILEPATH_FILE %\
                    {"bacula_name" : self.fileset.bacula_name}
            self.assertMultiLineEqual(content, template)

        filepath.delete()
        self.test_blank()

    def test_remove(self):
        self.fileset.delete()
        self.assertFalse(os.path.exists(self.filename))


    def test_wildcards(self):

        filepath = models.FilePath(path=u"/nimbus",
                                   fileset=self.fileset)
        filepath.save()

        wildcard_1 = models.Wildcard(kind="I",
                                     expression="*.exe",
                                     fileset=self.fileset)
        wildcard_1.save()
        wildcard_2 = models.Wildcard(kind="E",
                                     expression="*.avi",
                                     fileset=self.fileset)
        wildcard_2.save()

        with file(self.filename) as f_obj:
            content = f_obj.read()
            template = EXPECTED_FILTERS_FILE %\
                    {"bacula_name" : self.fileset.bacula_name}
            self.assertMultiLineEqual(content, template)


        wildcard_2.delete()

        with file(self.filename) as f_obj:
            content = f_obj.read()
            template = EXPECTED_FILTERS_FILE_2 %\
                    {"bacula_name" : self.fileset.bacula_name}
            self.assertMultiLineEqual(content, template)

        wildcard_1.delete()
        filepath.delete()


        self.test_blank()

