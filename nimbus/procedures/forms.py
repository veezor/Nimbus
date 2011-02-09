# -*- coding: utf-8 -*-

from nimbus.procedures.models import *
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        widgets = {
            'name': forms.widgets.TextInput(attrs={'class': 'text small'}),
            'storage': forms.widgets.Select(attrs={'class': 'styled'}),
            'schedule': forms.widgets.Select(attrs={'class': 'styled'}),
            'fileset': forms.widgets.Select(attrs={'class': 'styled'}),
        }