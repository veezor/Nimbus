#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.forms import ModelForm
from django.db import models

from nimbus.shared.fields import CharFormField


def make_custom_charfield(f):
    if isinstance(f, models.CharField):
        return f.formfield(form_class=CharFormField)
    else:
        return f.formfield()


def form(modelcls):

    class Form(ModelForm):

        formfield_callback = make_custom_charfield

        class Meta:
            model = modelcls

    return Form


