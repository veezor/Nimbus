#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.forms import PasswordInput
from django import forms

from nimbus.shared.fields import CharFormField

__all__ = ('StorageForm')

class StorageForm(forms.ModelForm):
    name = CharFormField(label=u"Name", max_length=255)
    address = CharFormField(label=u"Address", max_length=15)
    password = CharFormField(label=u"Password", widget=PasswordInput)
    description = CharFormField(label=u"Description", max_length=500)
