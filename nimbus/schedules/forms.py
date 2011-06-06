# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import inlineformset_factory, BaseInlineFormSet

#from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from nimbus.schedules import models
from nimbus.shared import forms as nimbus_forms

# class TriggerBaseForm(BaseInlineFormSet):
# 
#     def add_fields(self, form, index):
#         super(TriggerBaseForm, self).add_fields(form, index)
#         form.fields['active'] = forms.BooleanField()
# 
# 
# def make_form(modeltype, exclude_fields=None):
# 
#     class Form(forms.ModelForm):
#         formfield_callback = nimbus_forms.make_custom_fields
#         class Meta:
#             model = modeltype
#             exclude = exclude_fields
# 
#     return Form

class ScheduleForm(forms.ModelForm):
    name = forms.CharField(label="Nome do agendamento", widget=forms.TextInput(attrs={'class':'text small'}))
    class Meta:
        model = models.Schedule


class MonthForm(forms.ModelForm):
    active = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'schedule_activate', 'id': 'month'}))
    hour = forms.CharField(label="Hora", widget=forms.TextInput(attrs={'class':'text small mascara_hora'}))
    days = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = models.Month


class HourForm(forms.ModelForm):
    active = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'schedule_activate', 'id': 'hour'}))
    minute = forms.CharField(label=u'Minuto', widget=forms.TextInput(attrs={'class':'text small mascara_minuto'}))
    class Meta:
        model = models.Hour


class WeekForm(forms.ModelForm):
    active = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'schedule_activate', 'id': 'week'}))
    hour = forms.CharField(label=u'Hora', widget=forms.TextInput(attrs={'class':'text small mascara_hora'}))
    days = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = models.Week


class DayForm(forms.ModelForm):
    active = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'schedule_activate', 'id': 'day'}))
    hour = forms.CharField(label=u'Hora', widget=forms.TextInput(attrs={'class':'text small mascara_hora'}))
    class Meta:
        model = models.Day

#MonthForm = make_form(models.Month)
#DayForm = make_form(models.Day)
#HourForm = make_form(models.Hour)
#WeekForm = make_form(models.Week)

# class FormContainer(object):
# 
#     def __init__(self, instance=None, **form_classes):
#         self.form_classes = form_classes
#         self.forms = {}
#         self.instances = {}
#         self.instance = instance
# 
# 
#     def set_instances(self, **instances):
#         self.instances = instances
# 
#     def __getitem__(self, item):
#         return self.forms[item]
# 
#     def __setitem__(self, key, value):
#         self.forms[key] = value
# 
#     def __iter__(self):
#         return iter(self.forms)
# 
# 
#     def is_valid(self):
#         return all([ form.is_valid() for form in self.forms.values()])
# 
# 
#     def save(self):
#         result = {}
#         for name, form in self.forms.items():
#             result[name] = form.save()
# 
#         return result
# 
# 
#     def post(self, post_data):
#         for name, FormClass in self.form_classes.items():
#             instance = self.instances.get(name, None)
#             self.forms[name] = FormClass(post_data, prefix=name, instance=instance)
# 
# 
#     def get(self):
#         for name, FormClass in self.form_classes.items():
#             instance = None
# 
#             if self.instance:
#                 try:
#                     instance = getattr(self.instance, name)
#                 except ObjectDoesNotExist: #DoesNotExist baseclass
#                     pass
# 
#             self.forms[name] = FormClass(prefix=name, instance=instance)
# 
# 
# 
# def make_schedule_form_container(instance=None):
#     return FormContainer(
#         instance,
#         week = WeekForm,
#         month = MonthForm,
#         day = DayForm,
#         hour = HourForm
#     )