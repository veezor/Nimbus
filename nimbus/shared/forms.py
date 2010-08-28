#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django import forms
from django.db import models

from nimbus.shared.fields import CharFormField, IPAddressField

SELECT_ATTRS = {"class": "styled"}


def make_custom_fields(f, *args, **kwargs):
    # import pdb; pdb.set_trace()
    
    if f.choices:
        kwargs.pop('widget', None)
        return f.formfield(widget=forms.Select(attrs=SELECT_ATTRS), **kwargs)
    if isinstance(f, models.IPAddressField):
        return f.formfield(form_class=IPAddressField, **kwargs)
    elif isinstance(f, models.CharField):
        return f.formfield(form_class=CharFormField, **kwargs)
    elif isinstance(f, models.ManyToManyField):
        kwargs.pop('widget', None)
        return f.formfield(widget=forms.SelectMultiple(attrs=SELECT_ATTRS), **kwargs)
    else:
        return f.formfield(**kwargs)


def form(modelcls):

    class Form(forms.ModelForm):

        formfield_callback = make_custom_fields

        class Meta:
            model = modelcls

    return Form


