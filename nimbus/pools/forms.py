# -*- coding: utf-8 -*-

from pools.models import *
from django import forms

class PoolForm(forms.ModelForm):
    class Meta:
        model = Pool
        widgets = {
            'name': forms.widgets.TextInput(attrs={'class': 'text small'}),
            'size': forms.widgets.TextInput(attrs={'class': 'text small'}),
            'retention_time': forms.widgets.TextInput(attrs={'class': 'text small'}),
        }

