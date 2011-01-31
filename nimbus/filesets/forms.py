# -*- coding: utf-8 -*-

from nimbus.filesets.models import *
from django import forms


class FileSetForm(forms.ModelForm):
    class Meta:
        model = FileSet


class FilePathForm(forms.ModelForm):
    class Meta:
        model = FilePath