#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.offsite.models import Offsite
from nimbus.shared.forms import make_custom_fields
from django import forms


class OffsiteForm(forms.ModelForm):
    password = forms.CharField(required=False, initial='none',
                            widget=forms.PasswordInput(attrs={'class': 'text'}))
    active_upload_rate = forms.BooleanField(label="Ativar Taxa de Upload",
                                            required=False, initial=False)
    rate_limit = forms.CharField(label="Taxa de Upload (kb/s)", required=False,
                                initial=-1,
                                widget=forms.TextInput(attrs={'class': 'text'}))
    formfield_callback = make_custom_fields

    class Meta:
        model = Offsite
        fields = ('active', 'username', 'password', 'active_upload_rate',
                  'rate_limit')


class OffsiteRecoveryForm(forms.ModelForm):
    active = forms.BooleanField(required=False, initial=True,
                                widget=forms.HiddenInput())
    password = forms.CharField(required=False, initial='none',
                            widget=forms.PasswordInput(attrs={'class': 'text'}))
    active_upload_rate = forms.BooleanField(label="Ativar Taxa de Upload", 
                                            required=False, initial=False)
    upload_rate = forms.CharField(label="Taxa de Upload (kb/s)", required=False,
                                initial=-1,
                                widget=forms.TextInput(attrs={'class': 'text'}))
    formfield_callback = make_custom_fields

    class Meta:
        model = Offsite
        fields = ('active', 'username', 'password', 'active_upload_rate',
                  'upload_rate')
