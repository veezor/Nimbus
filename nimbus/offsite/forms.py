#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.offsite.models import Offsite
from nimbus.shared.forms import make_custom_fields
from django import forms


class OffsiteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'text small'})) 

    formfield_callback = make_custom_fields

    class Meta:
        model = Offsite
