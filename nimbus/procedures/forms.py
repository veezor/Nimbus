# -*- coding: utf-8 -*-

from django.db.models import Q
from nimbus.procedures.models import *
from django import forms
from django.utils.translation import ugettext as _


class ProcedureForm(forms.ModelForm):

    def __init__(self, data=None, *args, **kwargs):
        super(ProcedureForm, self).__init__(data, *args, **kwargs)
        # Se houver apenas uma opcao num ChoiceField a opção NULL sera removida
        for field in self.fields:
            if isinstance(self.fields[field], forms.models.ModelChoiceField):
                if len(self.fields[field].choices) == 1:
                    remove_null_choice(self, [field])

    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"), min_value=1, max_value=3650, widget=forms.HiddenInput())
    fileset = forms.models.ModelChoiceField(label=_("Fileset"),
                                queryset=FileSet.objects.filter(is_model=True))
    schedule = forms.models.ModelChoiceField(label=_("Schedule"),
                                queryset=Schedule.objects.filter(is_model=True))

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
        remove_null_choice(self, ['schedule', 'fileset', 'storage', 'computer'])
                                                
    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"),
                                             min_value=1, max_value=3650, widget=forms.HiddenInput())
                                
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


def remove_null_choice(current_form, fields):
    for field in fields:
        choices = []
        for choice in current_form.fields[field].choices:
            if choice[0] != u'':
                choices.append(choice)
        current_form.fields[field].choices = choices

