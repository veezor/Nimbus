#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.offsite.models import Offsite
from nimbus.shared.forms import make_custom_fields
from django import forms


class OffsiteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'text'})) 
    hour = forms.CharField(widget=forms.TextInput(attrs={'class': 'text'})) 
    upload_rate = forms.CharField(widget=forms.TextInput(attrs={'class': 'text'})) 

    formfield_callback = make_custom_fields

    class Meta:
        model = Offsite
        fields = ('active', 'username', 'password', 'gateway_url', 'hour', 'upload_rate')
