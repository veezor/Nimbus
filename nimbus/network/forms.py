#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.forms import ModelForm, ValidationError

from nimbus.network.models import NetworkInterface
from nimbus.shared.forms import make_custom_fields

class NetworkForm(ModelForm):


    def clean_dns2(self):
        data = self.cleaned_data['dns2']
        if data == "":
            data = self.cleaned_data['dns1']
        return data

    formfield_callback = make_custom_fields
    class Meta:
        model = NetworkInterface
