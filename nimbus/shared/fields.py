#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from django import forms
from django.db import models
from django.core.exceptions import ValidationError


path_re = re.compile('^([a-zA-Z]:)?/([a-zA-Z0-9 .@_-]+/?)*$')
NAME_RE = re.compile("^[\w\s]{4,255}$")


def check_model_name(value):
    if not NAME_RE.match(value):
        raise ValidationError("Campo não pode conter acentos. Limite mínimo de caracteres é 4")



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

class ChoiceField(forms.ChoiceField):
    
    def widget_attrs(self, widget):
        attrs = super(ChoiceField, self).widget_attrs(widget)
        import pdb; pdb.set_trace()
        return attrs

class Select(forms.Select):

    def widget_attrs(self, widget):
        attrs = super(ComboField, self).widget_attrs(widget)
        import pdb; pdb.set_trace()
        return attrs
