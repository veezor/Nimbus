# -*- coding: UTF-8 -*-

from nimbus.backup import models
from django import forms
from django.forms import widgets
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from nimbus.shared import forms as nimbus_forms


class TriggerBaseForm(BaseInlineFormSet):

    def add_fields(self, form, index):
        super(TriggerBaseForm, self).add_fields(form, index)
        form.fields['active'] = forms.BooleanField()


def make_form(modeltype, exclude_fields=None):

    class Form(forms.ModelForm):
        formfield_callback = nimbus_forms.make_custom_fields
        class Meta:
            model = modeltype
            exclude = exclude_fields
    return Form


class ProcedureForm(forms.ModelForm):
    name = forms.CharField(label=u"Nome do Procedimento", widget=widgets.TextInput(attrs={'class': 'text'}))
    offsite_on = forms.BooleanField(label=u"Ativar Backup Offsite", required=False)
    retention_time = forms.CharField(label=u"Tempo de Retenção (em dias)", widget=widgets.TextInput(attrs={'class': 'text small'}))

    class Meta:
        model = models.Procedure


class ScheduleForm(forms.ModelForm):
    name = forms.CharField(label=u"Nome do Agendamento", widget=widgets.TextInput(attrs={'class': 'text small'}))
    formfield_callback = nimbus_forms.make_custom_fields
    class Meta:
        model = models.Schedule


class FileSetForm(forms.ModelForm):
    name = forms.CharField(label=u"Nome", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = models.FileSet


class FilePathForm(forms.ModelForm):
    path = forms.CharField(label=u"Arquivos", widget=widgets.TextInput(attrs={'class': 'text small'}))
    class Meta:
        model = models.FilePath


class FormContainer(object):

    def __init__(self, **form_classes):
        self.form_classes = form_classes
        self.forms = {}
        self.instances = {}

    def set_instances(self, **instances):
        self.instances = instances

    def __getitem__(self, item):
        return self.forms[item]

    def __setitem__(self, key, value):
        self.forms[key] = value

    def __iter__(self):
        return iter(self.forms)

    def is_valid(self):
        return all([ form.is_valid() for form in self.forms.values()])


    def save(self):
        result = {}
        for name, form in self.forms.items():
            result[name] = form.save()
        return result

    def post(self, post_data):
        for name, FormClass in self.form_classes.items():
            instance = self.instances[name]
            self.forms[name] = FormClass(post_data, prefix=name, instance=instance)

    def get(self):
        for name, FormClass in self.form_classes.items():
            self.forms[name] = FormClass(prefix=name)


def make_schedule_form_container():
    return FormContainer(
        week = WeekForm,
        month = MonthForm,
        day = DayForm,
        hour = HourForm
    )


FilesFormSet = forms.models.inlineformset_factory(models.FileSet, models.FilePath, can_delete=False, extra=1)
Procedure = make_form(models.Procedure)
Pool = make_form(models.Pool, exclude_fields=["name"])
MonthForm = make_form(models.Month)
DayForm = make_form(models.Day)
HourForm = make_form(models.Hour)
WeekForm = make_form(models.Week)
