#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from nimbus.base.models import BaseModel
from nimbus.shared import utils, signals
from nimbus.libs.template import render_to_file

# Create your models here.

class FilePath(models.Model):
    path = models.FilePathField(max_length=255, null=False, unique=True)

    def __unicode__(self):
        return self.path



class FileSet(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False)
    files = models.ManyToManyField(FilePath)

    def __unicode__(self):
        return self.name


def update_fileset_file(fileset):
    """FileSet update filesets to a procedure instance"""

    name = fileset.bacula_name()

    filename = path.join( settings.NIMBUS_FILESETS_PATH, 
                          name)

    render_to_file( filename,
                    "fileset",
                    name=name,
                    files=[ f.path for f in fileset.paths_set.all() ])




def remove_fileset_file(fileset):
    """remove FileSet file"""

    name = fileset.bacula_name()
    filename = path.join( settings.NIMBUS_FILESETS_PATH, 
                          name)
    utils.remove_or_leave(filename)    




signals.connect_on( update_fileset_file, FileSet, post_save)
signals.connect_on( remove_fileset_file, FileSet, post_delete)
