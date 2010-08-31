#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import forms
from django.db import models

from nimbus.storages.models import Storage
# from nimbus.shared.fields import CharFormField
from nimbus.shared.forms import make_custom_fields

__all__ = ('StorageForm')

class StorageForm(forms.ModelForm):
    formfield_callback = make_custom_fields
    
    name = forms.CharField(label=u"Name", max_length=255)
    address = forms.CharField(label=u"Address", max_length=15)
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)
    description = forms.CharField(label=u"Description", max_length=500)
    
    class Meta:
        model = Storage
    