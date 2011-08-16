#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import forms

from nimbus.reports.models import EmailConf


class EmailConfForm(forms.ModelForm):
    password = forms.CharField(label=u'Senha',widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = EmailConf

