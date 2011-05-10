#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete, m2m_changed

from nimbus.base.models import BaseModel
from nimbus.shared import utils, signals, fields
from nimbus.computers import models as computer_models
from nimbus.libs.template import render_to_file
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^nimbus\.shared\.fields\.ModelPathField"])

class FileSet(BaseModel):
    name = models.CharField(max_length=255, unique=True, null=False,
                            validators=[fields.check_model_name])

    def __unicode__(self):
        return self.name


class FilePath(models.Model):
    computer = models.ForeignKey(computer_models.Computer)
    path = fields.ModelPathField(max_length=2048, null=False)
    filesets = models.ForeignKey(FileSet, related_name="files", null=True,
                                 blank=True)


def update_fileset_file(fileset):
    """FileSet update filesets to a procedure instance"""
    name = fileset.bacula_name
    filename = path.join(settings.NIMBUS_FILESETS_DIR, name)
    render_to_file(filename, "fileset", name=name,
                   files=[f.path for f in fileset.files.all()])


def remove_fileset_file(fileset):
    """remove FileSet file"""
    name = fileset.bacula_name
    filename = path.join(settings.NIMBUS_FILESETS_DIR, name)
    utils.remove_or_leave(filename)    


def update_filepath(obj):
    if isinstance(obj, FilePath):
        for fileset in obj.filesets.all():
            update_fileset_file(fileset)
    elif isinstance(obj, FileSet):
        update_fileset_file(obj)
    else:
        # TODO: TRATAR
        pass


signals.connect_on(update_fileset_file, FileSet, post_save)
signals.connect_on(remove_fileset_file, FileSet, post_delete)