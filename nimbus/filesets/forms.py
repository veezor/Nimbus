# -*- coding: utf-8 -*-

from nimbus.filesets.models import *
from django import forms
from django.forms import widgets
from nimbus.shared import forms as nimbus_forms


class FileSetForm(forms.ModelForm):
    name = forms.CharField(label=u"Nome", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = FileSet


class FilePathForm(forms.ModelForm):
    path = forms.CharField(label=u"Arquivos", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = FilePath
    

FilesFormSet = forms.models.inlineformset_factory(FileSet, FilePath, can_delete=False, extra=0)
