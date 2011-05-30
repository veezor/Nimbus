# -*- coding: utf-8 -*-

from nimbus.procedures.models import *
from django import forms

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        widgets = {'name': forms.widgets.TextInput(attrs={'class': 'text small'}),
                   'storage': forms.widgets.Select(attrs={'class': 'styled'}),
                   'schedule': forms.widgets.Select(attrs={'class': 'styled'}),
                   'fileset': forms.widgets.Select(attrs={'class': 'styled'})}


class ProcedureForm(forms.ModelForm):

    pool_retention_time = forms.IntegerField(
                                    label="Tempo de validade do backup (dias)",
                                    min_value=1, max_value=3650)

    class Meta:
        model = Procedure
        fields = ('computer',
                  'schedule',
                  'fileset',
                  'storage',
                  'pool_retention_time',
                  'name')
        exclude = ('active', 'pool_size', 'pool_name')