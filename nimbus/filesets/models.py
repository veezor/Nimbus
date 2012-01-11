#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from os import path

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from nimbus.base.models import BaseModel
from nimbus.shared import utils, signals, fields
from nimbus.computers import models as computer_models
from nimbus.libs.template import render_to_file



class FileSet(BaseModel):
    name = models.CharField(max_length=255, null=False)
    is_model = models.BooleanField(default=False, blank=True)    

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name = u"Conjunto de arquivos"
        
    @property
    def includes(self):
        result =[]
        for w in self.wildcards.all():
            if w.kind == 'I':
                result.append(w)
        return result
    
    @property
    def excludes(self):
        result =[]
        for w in self.wildcards.all():
            if w.kind == 'E':
                result.append(w)
        return result
        

class FilePath(models.Model):
    path = fields.ModelPathField(max_length=2048, null=False)
    fileset = models.ForeignKey(FileSet, related_name="files", null=False,
                                 blank=False)

    def __unicode__(self):
        return u"%s - %s" % (self.fileset.name, self.path)

    class Meta:
        verbose_name = u"Arquivo"


class Wildcard(models.Model):
    kind = models.CharField(max_length=1, null=False) # 'E' for exclude, 'I' for Include
    expression = models.CharField(max_length=255, null=False)
    fileset = models.ForeignKey(FileSet, related_name="wildcards", null=False,
                                 blank=False)

    def __unicode__(self):
        if self.kind.upper() == 'E':
            return "Exclude: '%s'" % self.expression
        else:
            return "Include: '%s'" % self.expression

    class Meta:
        verbose_name = u"Filtro"            

def update_fileset_file(fileset):
    """FileSet update filesets to a procedure instance"""
    name = fileset.bacula_name
    verbose_name = fileset.name
    filename = path.join(settings.NIMBUS_FILESETS_DIR, name)
    files = [f.path for f in fileset.files.all()]
    includes = [w.expression for w in fileset.includes]
    excludes = [w.expression for w in fileset.excludes]
    render_to_file(filename, "fileset", name=name, files=files,
                   includes=includes, excludes=excludes,
                   verbose_name=verbose_name)

def update_filters(wildcard):
    fileset = wildcard.fileset
    update_fileset_file(fileset)

def remove_fileset_file(fileset):
    """remove FileSet file"""
    name = fileset.bacula_name
    filename = path.join(settings.NIMBUS_FILESETS_DIR, name)
    utils.remove_or_leave(filename)    


def update_filepath(filepath):
    update_fileset_file(filepath.fileset)


signals.connect_on(update_fileset_file, FileSet, post_save)
signals.connect_on(update_filepath, FilePath, post_save)
signals.connect_on(update_filters, Wildcard, post_save)
signals.connect_on(remove_fileset_file, FileSet, post_delete)
signals.connect_on(update_filepath, FilePath, post_delete)
