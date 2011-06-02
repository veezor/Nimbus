# -*- coding: utf-8 -*-

from django.db.models import Q
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

import pdb
class ProcedureEditForm(forms.ModelForm):
    
    def __init__(self, data=None, *args, **kwargs):
        super(ProcedureEditForm, self).__init__(data, *args, **kwargs)
        instance = kwargs.get("instance")
        f_id = instance.fileset.id
        self.fields['fileset'] = forms.models.ModelChoiceField(
                                            label=_("Fileset"), required=False,
                                            queryset=FileSet.objects.filter(
                                                Q(is_model=True) | Q(id=f_id)))
        s_id = instance.schedule.id
        self.fields['schedule'] = forms.models.ModelChoiceField(
                                            label=_("Schedule"), required=False,
                                            queryset=Schedule.objects.filter(
                                                Q(is_model=True) | Q(id=s_id)))
        self.remove_null_choice()
                                                
    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"),
                                             min_value=1, max_value=3650)
                                
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
    
    def remove_null_choice(self):
        for field in ['schedule', 'fileset']:
            choices = []
            for choice in self.fields[field].choices:
                if choice[0] != u'':
                    choices.append(choice)
            self.fields[field].choices = choices

