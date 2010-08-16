#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re

from django import forms
from django.db import models


path_re = re.compile('^([a-zA-Z]:)?/([a-zA-Z0-9 .@_-]+/?)*$')

class FormPathField(forms.CharField):
    def clean(self, value):
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
        
        if self.max_length < 20:
            attrs['class'] = 'text small'
        elif self.max_length < 200:
            attrs['class'] = 'text medium'
        else:
            attrs['class'] = "text"
            
        return attrs
        
