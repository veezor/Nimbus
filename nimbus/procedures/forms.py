# -*- coding: utf-8 -*-

from nimbus.procedures.models import *
from django import forms
from django.utils.translation import ugettext as _
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet


class ProcedureForm(forms.ModelForm):

    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"), min_value=1, max_value=3650)
    # limita a exibicao apenas aos objetos que forem Modelo (is_model=True)
    fileset = forms.models.ModelChoiceField(label=_("Fileset"), queryset=FileSet.objects.filter(is_model=True))
    schedule = forms.models.ModelChoiceField(label=_("Schedule"), queryset=Schedule.objects.filter(is_model=True))

    class Meta:
        model = Procedure
        fields = ('computer',
                  'schedule',
                  'fileset',
                  'storage',
                  'pool_retention_time',
                  'name')
        exclude = ('active', 'pool_size', 'pool_name')


class ProcedureEditForm(forms.ModelForm):

    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"), min_value=1, max_value=3650)
    fileset = forms.models.ModelChoiceField(label=_("Fileset"), queryset=FileSet.objects.filter(is_model=True))
    schedule = forms.models.ModelChoiceField(label=_("Schedule"), queryset=Schedule.objects.filter(is_model=True))

    class Meta:
        model = Procedure
        fields = ('active',
                  'name',
                  'computer',
                  'schedule',
                  'fileset',
                  'storage',
                  'pool_retention_time')
        exclude = ('pool_size', 'pool_name')

