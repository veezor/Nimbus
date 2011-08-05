#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pytz import country_timezones

from django import forms
from django.forms import ModelForm, ValidationError
from nimbus.timezone.models import Timezone, COUNTRY_CHOICES
from nimbus.shared.forms import make_custom_fields


class TimezoneForm(ModelForm):
    area = forms.ChoiceField(label='Região', choices=[('', '----------')],
            widget=forms.Select(attrs={'class': 'uniform'}))
    country = forms.ChoiceField(label='País', choices=COUNTRY_CHOICES,
            widget=forms.Select(attrs={'class': 'uniform'}))

    formfield_callback = make_custom_fields

    def __init__(self, data=None, *args, **kwargs):
        super(TimezoneForm, self).__init__(data, *args, **kwargs)

        instance = kwargs.get("instance")
        if instance:
            self.load_area(instance.country)
        if data:
            self.load_area( data.get("country") )

    class Meta:
        model = Timezone
        exclude = ("uuid",)
    
    def load_area(self, country=None):
        if country:
            self.fields['area'].choices = \
                [ (a,a) for a in sorted(country_timezones[country])]
        else:
            self.fields['area'].choices = [('', '----------')]


    def clean_area(self):
        area = self.data.get("area")
        country = self.data.get("country")
        if area in country_timezones[country]:
            return area
        else:
            raise ValidationError("error")


