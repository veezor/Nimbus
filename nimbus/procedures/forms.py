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
                not_model_filter(field, self.fields[field])
                if field not in ['schedule', 'fileset']:
                    remove_null_choice(self.fields[field])
                else:
                    self.fields[field].empty_label = u"-ou escolha um perfil-"

    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"),
                                             min_value=1, max_value=3650,
                                             initial=10,
                                             widget=forms.HiddenInput())
    fileset = forms.models.ModelChoiceField(label=_("Fileset"),
                                            queryset=FileSet.objects.all(),
                                            empty_label = u"-ou escolha um perfil-")
    schedule = forms.models.ModelChoiceField(label=_("Schedule"),
                                             queryset=Schedule.objects.all(),
                                             empty_label = u"-ou escolha um perfil-")
    # fileset.empty_label = u"-ou escolha um modelo-"
    # schedule.empty_label = u"-ou escolha um modelo-"

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
#        remove_null_choice(self, ['schedule', 'fileset', 'storage', 'computer'])
                                                
    pool_retention_time = forms.IntegerField(label=_("Retention Time (days)"),
                                             min_value=1, widget=forms.HiddenInput())
                                
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


def remove_null_choice(field_object):
    current_choices = field_object.choices
    if len(current_choices) == 1:
        choices = []
        for choice in current_choices:
            if choice[0] != u'':
                choices.append(choice)
        field_object.choices = choices


def not_model_filter(field_name, field_object):
    # choice_forms = [{'field': 'schedule', 'object': Schedule},
    #          {'field': 'fileset', 'object': FileSet}]
    # for cform in choice_forms:
    choice_forms = {'schedule': Schedule, 'fileset': FileSet}
    if choice_forms.has_key(field_name):    
        choices = []
        current_choices = field_object.choices
        for choice in current_choices:
            if choice[0] != u'':
                if choice_forms[field_name].objects.get(id=choice[0]).is_model:
                    choices.append(choice)
            else:
                choices.append(choice)
        field_object.choices = choices
