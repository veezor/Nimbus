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
def friendly_level(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        if obj == 'I':  return 'Incremental'
        elif obj == 'F': return 'Completo'
        else: return 'Desconhecido'
    else:
        return ''


@register.filter
def get_method(obj, value):
    """ Try to get an attribute from an object.
    Example: 
    """
    return getattr(obj, value)
    
    
@register.filter
def restriction_value(rtime_object, day_name):
    """ Get restriction value for day of the week if exists.
    Example: 
    """
    from backup_corporativo.bkp.models import BandwidthRestriction, DayOfTheWeek, RestrictionTime
    
    try:
        day_object = DayOfTheWeek.objects.get(day_name=day_name)
        rest = rtime_object.bandwidthrestriction_set.filter(dayoftheweek=day_object)
        rest = rest and rest[0] or False
        return rest and rest.restriction_value or '----'
    except Exception:
        return ''
        
@register.filter
def restriction_id(rtime_object, day_name):
    """ Get restriction id for day of the week if exists.
    Example: 
    """
    from backup_corporativo.bkp.models import BandwidthRestriction, DayOfTheWeek, RestrictionTime
    
    try:
        day_object = DayOfTheWeek.objects.get(day_name=day_name)
        rest = rtime_object.bandwidthrestriction_set.filter(dayoftheweek=day_object)
        rest = rest and rest[0] or False
        return rest and rest.id or ''
    except Exception:
        return ''