#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from nimbus.shared.forms import form
from nimbus.storages.models import Storage
from nimbus.procedures.models import Procedure

StorageForm = form(Procedure)

# class StorageForm(forms.ModelForm):
#     name = CharFormField(label=u"Name", max_length=255)
#     address = CharFormField(label=u"Address", max_length=15)
#     password = CharFormField(label=u"Password", widget=PasswordInput)
#     description = CharFormField(label=u"Description", max_length=500)