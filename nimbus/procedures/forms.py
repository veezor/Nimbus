# -*- coding: utf-8 -*-

import re

from django.db.models import Q
from nimbus.procedures.models import *
from django import forms
from django.utils.translation import ugettext_lazy as _


class ProcedureForm(forms.ModelForm):

    def __init__(self, data=None, *args, **kwargs):
        super(ProcedureForm, self).__init__(data, *args, **kwargs)
        p = Procedure.objects.filter(name__startswith="Backup #").order_by("id")
        if p:
            index_string = p[len(p) - 1].name.split("#")[1]
            match = re.search("(\d+)", index_string)
            if match:
                next_id = int(match.group()) + 1
            else:
                next_id = 1
        else:
            next_id = 1
        name_sugestion = "Backup #%02d" % next_id
        self.fields['name'] = forms.CharField(initial=name_sugestion)
        # Se houver apenas uma opcao num ChoiceField a opção NULL sera removida
        for field in self.fields:
            if isinstance(self.fields[field], forms.models.ModelChoiceField):
                not_model_filter(field, self.fields[field])
                if field not in ['schedule', 'fileset']:
                    remove_null_choice(self.fields[field])
                else:
                    self.fields[field].empty_label =_(u"-or choose a profile-")


    computer = forms.models.ModelChoiceField(label=_("Computer"),
                                             queryset=Computer.objects.filter(id__gt=1).filter(active=True))
    # name = forms.CharField(initial=self.name_sugestion)

    pool_retention_time = forms.IntegerField(label=_("Retention time"),
                                             min_value=1, max_value=9999,
                                             initial=10)
                                             # widget=forms.HiddenInput())
    fileset = forms.models.ModelChoiceField(label=_("File sets"),
                                            queryset=FileSet.objects.filter(id__gt=1),
                                            empty_label = _(u"-or choose a profile-"))
    schedule = forms.models.ModelChoiceField(label=_("schedule"),
                                             queryset=Schedule.objects.filter(id__gt=1),
                                             empty_label = _(u"-or choose a profile-"))

    class Meta:
        model = Procedure
        fields = ('computer',
                  'schedule',
                  'fileset',
                  'storage',
                  'pool_retention_time',
                  'name',
                  'job_tasks')
        exclude = ('active', 'pool_size', 'pool_name')
        widgets = {'job_tasks': forms.CheckboxSelectMultiple()}


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
                                                
    pool_retention_time = forms.IntegerField(label=_("Retention time"),
                                             min_value=1, max_value=9999)
                                             # widget=forms.HiddenInput())
                                
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
