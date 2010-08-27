#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.forms import ModelForm
from django.db import models

from nimbus.shared.fields import CharFormField, IPAddressField


def make_custom_fields(f):
    # import pdb; pdb.set_trace()
    if isinstance(f, models.CharField):
        return f.formfield(form_class=CharFormField)
    elif isinstance(f, models.IPAddressField):
        return f.formfield(form_class=IPAddressField)
    else:
        return f.formfield()


def form(modelcls):

    class Form(ModelForm):

        formfield_callback = make_custom_fields

        class Meta:
            model = modelcls

    return Form


