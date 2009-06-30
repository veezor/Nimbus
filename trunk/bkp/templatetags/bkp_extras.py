#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()



@register.filter
def get_trigger_level(obj):
    """ Try to get an attribute from an object.
    Example: {% schedule|get_trigger_level %}

    """
    trigg = obj.get_trigger()
    
    if trigg:
       return trigg.level
    else:
        return ''


@register.filter
def get_trigger_hour(obj):
    """ Try to get an attribute from an object.
    Example: {% schedule|get_trigger_level %}

    """
    trigg = obj.get_trigger()
    
    if trigg:
       return trigg.hour
    else:
        return ''


@register.filter
def get_id(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj[0]
    else:
        return ''

@register.filter
def get_client_source(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj[2]
    else:
        return ''

@register.filter
def get_client_restore(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj[2]
    else:
        return ''
        
@register.filter
def get_date(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj[6]
    else:
        return ''

        
@register.filter
def get_fileset(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj[1]
    else:
        return ''


@register.filter
def successful(obj):
    """ Try to get an attribute from an object.
    Example: 
    """
    if obj:
        return  obj[5] == 'T'
    else:
        return ''


@register.filter
def get_method(obj, value):
    """ Try to get an attribute from an object.
    Example: 
    """
    return getattr(obj, value)