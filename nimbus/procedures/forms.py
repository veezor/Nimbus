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
   # name = forms.CharField(label=u"Nome do Procedimento", widget=forms.widgets.TextInput(attrs={'class': 'text'}))
   # offsite_on = forms.BooleanField(label=u"Ativar Backup Offsite", required=False)
   # retention_time = forms.CharField(label=u"Tempo de Retenção (em dias)", widget=forms.widgets.TextInput(attrs={'class': 'text small'}))

   class Meta:
       model = Procedure
