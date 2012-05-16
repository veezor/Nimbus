#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as __

from nimbus.reports.models import EmailConf


class EmailConfForm(forms.ModelForm):
    email_password = forms.CharField(label=__(u'Password'), required=False,
                                     widget=forms.PasswordInput(render_value=False))


    def is_valid(self):
        data = self.data.copy()
        if not 'active' in data:
            data['send_to'] = _('youruser@yourcompany.com')
            data['email_host'] = _('yourcompany.com')
            data['email_port'] = '25'
        self.data = data
        return super(EmailConfForm, self).is_valid()

    class Meta:
        model = EmailConf

