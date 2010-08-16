#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.forms import PasswordInput


from nimbus.shared.fields import CharFormField

class AuthForm(AuthenticationForm):
    username = CharFormField(label=_("Username"), max_length=30)
    password = CharFormField(label=_("Password"), widget=PasswordInput)
