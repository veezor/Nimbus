#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from django import forms
from django.db import models
from django.core.exceptions import ValidationError


path_re = re.compile('^([a-zA-Z]:)?/([a-zA-Z0-9 .@_-]+/?)*$')
NAME_RE = re.compile("^[\w\s]{4,255}$")



DOMAIN_RE = re.compile(
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def check_domain(value):
    if not DOMAIN_RE.match(value):
        raise ValidationError("must be a domain")




def check_model_name(value):
    if not NAME_RE.match(value):
        raise ValidationError("O campo deve conter apenas caracteres alfa-numéricos e espaços. O limite mínimo de caracteres é 4.")

def name_is_valid(value):
    try:
        check_model_name(value)
        return True
    except ValidationError, error:
        return False

class FormPathField(forms.CharField):
    def clean(self, value):
        super(FormPathField, self).clean(value)
        if not re.match(path_re, value):
            raise forms.ValidationError, u'Invalid format'
        return value


class ModelPathField(models.CharField):
    def formfield(self, *args, **kwargs):
        kwargs['form_class'] = FormPathField
        return super(ModelPathField, self).formfield(*args, **kwargs)



class CharFormField(forms.CharField):

    def widget_attrs(self, widget):
        attrs = super(CharFormField, self).widget_attrs(widget)

        if not attrs:
            attrs = {}

        # import pdb; pdb.set_trace()

        # if self.choices:
        #     attrs['class'] = 'styled'
        # else:
        if self.max_length < 40:
            attrs['class'] = 'text small'
        elif self.max_length < 260:
            attrs['class'] = 'text medium'
        else:
            attrs['class'] = "text big"

        return attrs

class IPAddressField(forms.IPAddressField):

    def widget_attrs(self, widget):

        attrs = super(IPAddressField, self).widget_attrs(widget)

        if not attrs:
            attrs = {}

        attrs['class'] = 'text small'

        return attrs

