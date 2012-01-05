# -*- coding: utf-8 -*-

from nimbus.filesets.models import *
from django import forms
from django.forms import widgets
from nimbus.shared import forms as nimbus_forms


class FileSetForm(forms.ModelForm):
    name = forms.CharField(label=u"Nome", widget=widgets.TextInput(attrs={'class': 'text small'}))
    # is_model = forms.BooleanField(widget=widgets.HiddenInput(attrs={'value': '0'}))
    class Meta:
        model = FileSet


class FilePathForm(forms.ModelForm):
    path = forms.CharField(label=u"Arquivo", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = FilePath

WildcardsFormSet = forms.models.inlineformset_factory(FileSet, Wildcard, can_delete=False, extra=0)
FilesFormSet = forms.models.inlineformset_factory(FileSet, FilePath, can_delete=False, extra=0)

class FilesToDeleteForm(FilesFormSet):
    
    def __init__(self, data=None, *args, **kwargs):
        super(FilesToDeleteForm, self).__init__(data, *args, **kwargs)
        for f in self.forms:
            f.fields['DELETE'].widget.attrs = {'class': 'no-style'}
            f.fields['path'].widget.attrs = {'readonly': 'readonly'}
            # f.fields['path'].widget = forms.HiddenInput()
            
    can_delete = True
    form = FilePathForm