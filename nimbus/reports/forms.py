#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import forms

from nimbus.reports.models import EmailConf


class EmailConfForm(forms.ModelForm):
    email_password = forms.CharField(label=u'Senha', required=False,
                                     widget=forms.PasswordInput(render_value=False))


    def is_valid(self):
        data = self.data.copy()
        if not 'active' in data:
            data['send_to'] = 'seuemail@suaempresa.com'
            data['email_host'] = 'suaempresa.com'
            data['email_port'] = '25'
        self.data = data
        return super(EmailConfForm, self).is_valid()

    class Meta:
        model = EmailConf

