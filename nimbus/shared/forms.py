#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import copy

from django import forms
from django.forms import widgets

from django.db import models

from nimbus.shared.fields import CharFormField, IPAddressField

SELECT_ATTRS = {"class": "style-select"}
INPUT_ATTRS = {"class":"text small"}

class InvalidMapping(Exception):
    pass



def make_custom_fields(f, *args, **kwargs):
    # import pdb; pdb.set_trace()
    
    if f.choices or isinstance(f, models.ForeignKey):
        kwargs.pop('widget', None)
        return f.formfield(widget=forms.Select(attrs=SELECT_ATTRS), **kwargs)
    if isinstance(f, models.IPAddressField):
        return f.formfield(form_class=IPAddressField, **kwargs)
    elif isinstance(f, models.CharField):
        return f.formfield(widget=widgets.TextInput(attrs=INPUT_ATTRS), **kwargs)
    elif isinstance(f, models.TimeField):
        return f.formfield(widget=widgets.TextInput(attrs=INPUT_ATTRS), **kwargs)
    elif isinstance(f, models.PositiveSmallIntegerField):
        return f.formfield(widget=widgets.TextInput(attrs=INPUT_ATTRS), **kwargs)
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



def form_from_model(model):
    formclass = form(model.__class__)
    f = formclass({}, instance=model)
    f.data.update( f.initial )
    return f

def form_mapping(modelcls, query_dict, fieldname_list=None, object_id=None):


    mapping_table = {}

    if not fieldname_list:
        clsname = modelcls.__name__.lower()
        fieldname_list = [ name for name in query_dict.keys() if name.startswith(clsname) ]

    meta = modelcls._meta
    modelfields = meta.get_all_field_names()
    modelfields.remove('id')


    fieldlist = copy.copy(modelfields)

    for field in fieldlist:
        try:
            fieldobj = meta.get_field(field)

            if not fieldobj.editable:
                modelfields.remove(field)

        except models.FieldDoesNotExist, error:
            modelfields.remove(field)


    modelfields = [ field for field in modelfields \
                        if not isinstance( meta.get_field(field), models.ManyToManyField) ]


    for field in fieldlist:
        for user_field_name in fieldname_list:
            if field in user_field_name:
                mapping_table[user_field_name] = field
                break


    if len(modelfields) != len(fieldname_list):
        raise InvalidMapping("Not match: %s != %s" % (modelfields, fieldname_list))


    data = {}

    for user_field_name,form_field_name in mapping_table.items():
        data[form_field_name] = query_dict[user_field_name]

    FormClass = form(modelcls)

    if object_id:
        instance = modelcls.objects.get(id=object_id)
        return FormClass(data, instance=instance)

    return FormClass(data)


