#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib import admin
from django import forms

from nimbus.filesets.models import FileSet, FilePath

class FilePathAdminForm(forms.ModelForm):
    path = forms.FilePathField(path="/",widget=forms.TextInput)

    class Meta:
        model = FilePath


class FilePathAdmin(admin.ModelAdmin):
    form = FilePathAdminForm
    




admin.site.register(FileSet)
admin.site.register(FilePath)
