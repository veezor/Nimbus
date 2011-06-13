# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from nimbus.schedules import models
from nimbus.shared import forms as nimbus_forms


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
    minute = forms.IntegerField(label="Minuto da hora",
                                min_value=0, max_value=59,
                                initial=00,
                                widget=forms.TextInput(attrs={'class':'text small'}))# mascara_minuto'}))
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

