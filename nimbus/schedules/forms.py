# -*- coding: utf-8 -*-

from nimbus.schedules.models import Schedule, Daily, Monthly, Hourly, Weekly
from django import forms


class ScheduleForm(forms.ModelForm):
    name = forms.CharField(label="Nome do agendamento",
                widget=forms.TextInput(attrs={'class':'text small'}))
    class Meta:
        model = Schedule


class DailyForm(forms.ModelForm):
    class Meta:
        model = Daily


class MonthlyForm(forms.ModelForm):
    class Meta:
        model = Monthly


class HourlyForm(forms.ModelForm):
    class Meta:
        model = Hourly


class WeeklyForm(forms.ModelForm):
    class Meta:
        model = Weekly
