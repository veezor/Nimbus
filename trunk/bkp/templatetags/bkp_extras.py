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
