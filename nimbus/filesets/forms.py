# -*- coding: utf-8 -*-

from nimbus.filesets.models import *
from django import forms
from django.forms import widgets


class FileSetForm(forms.ModelForm):
    name = forms.CharField(label=u'Nome', widget=widgets.TextInput(attrs={'class': 'text'}))
    class Meta:
        model = FileSet


class FilePathForm(forms.ModelForm):
    class Meta:
        model = FilePath
