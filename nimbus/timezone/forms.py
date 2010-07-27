#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pytz import country_timezones

from django.forms import ModelForm
from nimbus.timezone.models import Timezone


class TimezoneForm(ModelForm):

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


