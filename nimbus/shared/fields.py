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

