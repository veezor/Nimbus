#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from nimbus.offsite.models import Offsite
from django import forms


class OffsiteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput) 

    class Meta:
        model = Offsite
