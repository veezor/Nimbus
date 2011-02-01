#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.offsite.models import Offsite
from nimbus.shared.forms import make_custom_fields
from django import forms


class OffsiteForm(forms.ModelForm):
    password = forms.CharField(required=False, initial='none',
                     widget=forms.PasswordInput(attrs={'class': 'text'})) 

    upload_rate = forms.CharField(required=False, initial=-1,
                    widget=forms.TextInput(attrs={'class': 'text'})) 

    formfield_callback = make_custom_fields

    class Meta:
        model = Offsite
        fields = ('active', 'username', 'password', 'upload_rate')
