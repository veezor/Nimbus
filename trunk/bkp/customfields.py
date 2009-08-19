#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

###
###   Fields
###

path_re = re.compile('^([a-zA-Z]:)?/([a-zA-Z0-9 .@_-]+/)*$')
slug_re = re.compile('^[a-zA-Z0-9-_]+$')
mdayslist_re = re.compile('^([0-9]|[0-2][0-9]|3[0-1])(;([0-9]|[0-2][0-9]|3[0-1]))*$')

class FormSlugField(forms.CharField):
    def clean(self, value):
        if not re.match(slug_re, value):
            raise forms.ValidationError, u'Formato inválido: pode possuir apenas alfanuméricos, underscores ou hífens.'
        return value


class ModelSlugField(models.CharField):
    def formfield(self, *args, **kwargs):
        "Changing standard FormField"
        kwargs['form_class'] = FormSlugField
        return super(ModelSlugField, self).formfield(*args, **kwargs)



class FormPathField(forms.CharField):
    def clean(self, value):
        if not re.match(path_re, value):
            raise forms.ValidationError, u'Formato inválido: utilize apenas formato unix ou windows. ex.: /var/wwww/ ou C:/Dados/'
        return value


class ModelPathField(models.CharField):
    def formfield(self, *args, **kwargs):
        "Changing standard FormField"
        kwargs['form_class'] = FormPathField
        return super(ModelPathField, self).formfield(*args, **kwargs)
        
class FormMonthDaysListField(forms.CharField):
    def clean(self, value):
        if not re.match(mdayslist_re, value):
            raise forms.ValidationError, u'Formato inválido: Utilize dias do mês (máx: 29) separados por ponto e vírgula. ex.: 01;15;29'
        return value


class ModelMonthDaysListField(models.CharField):
    def formfield(self, *args, **kwargs):
        "Changing standard FormField"
        kwargs['form_class'] = FormMonthDaysListField
        return super(ModelMonthDaysListField, self).formfield(*args, **kwargs)

class FormFileNimbusField(forms.FileField):
	def clean(self, value, initial=None):
		if not value:
			raise forms.ValidationError, u'Nenhum arquivo selecionado.'

		extension = value.name.split(".")[-1]
		if extension != 'nimbus':
			raise forms.ValidationError, u'Extensão inválida, apenas arquivos \'.nimbus\' são aceitos.'
		return value
		
# Início MACAddressField
# Código adaptado a partir de: 
# http://www.djangosnippets.org/snippets/1337/


MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)

class MACAddressFormField(forms.fields.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(*args, **kwargs)

	def clean(self, value, initial=None):
		if not re.match(mac_re, value):
			raise forms.ValidationError, u'Nenhum arquivo selecionado.'			

class MACAddressField(models.Field):
    empty_strings_allowed = False
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ChoiceField"

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)


# Fim MACAddressField
