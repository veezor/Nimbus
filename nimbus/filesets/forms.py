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
    path = forms.CharField(label=u"Arquivo", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = FilePath
    

FilesFormSet = forms.models.inlineformset_factory(FileSet, FilePath, can_delete=False, extra=0)
# FilesToDeleteForm = forms.models.inlineformset_factory(FileSet, FilePath, form=FilePathForm, extra=0)

class FilesToDeleteForm(FilesFormSet):
    def __init__(self, data=None, *args, **kwargs):
        super(FilesToDeleteForm, self).__init__(data, *args, **kwargs)
        for f in self.forms:
            f.fields['DELETE'].widget.attrs = {'class': 'no-style'}
            # f.fields['path'].widget.attrs = {'disabled': 'disabled'}
            # f.fields['path'].widget = forms.HiddenInput()
            
    
    
    can_delete = True
    form = FilePathForm