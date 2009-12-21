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
def friendly_date(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  obj.strftime("%d-%m-%y")
    else:
        return ''


@register.filter
def friendly_hour(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    import time
    if obj:
        return  obj.strftime("%H:%M")
    else:
        return ''


@register.filter
def friendly_size_mb(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return  ("%s MB" % str(obj/(1024*1024)))
    else:
        return ''

@register.filter
def friendly_status(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        if obj == 'T':
            return "Sucesso"
        elif obj == 'E':
            return "Erro"
        elif obj == 'R':
            return "Executando"
        elif obj == 'e':
            return 'Erro não fatal'
        elif obj == 'f':
            return 'Erro fatal'
        elif obj == 'I':
            return 'Incompleto'
        else:
            return "Desconhecido"
    else:
        return ''

@register.filter
def friendly_duration_min(obj):
    """ Try to get an attribute from an object.
    Example: 

    """
    if obj:
        return "%s Min" % str(round(obj/60,2))
    else:
        return ''


@register.filter
def get_method(obj, value):
    """ Try to get an attribute from an object.
    Example: 
    """
    return getattr(obj, value)
    

@register.filter
def get_value(obj, key):
    """ Try to get an attribute from an object.
    Example: 
    """
    return key in obj and obj[key] or ''
    
    
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


@register.filter
def contains(obj, value):
    """Verify if a value is containned in an obj."""
    return value in obj


@register.filter
def isequal(obj, value):
    """Verify if a value is containned in an obj."""
    return value == obj


@register.filter
def isdir(obj):
    """Returns True if an obj ends with a '/'."""
    if isinstance(obj, str):
        return obj.endswith('/')
    else:
        return False

@register.filter
def isinstanceof(obj, value):
    return isinstance(obj, value)

@register.filter
def isinstanceofdict(obj):
    return isinstance(obj, dict)

@register.filter
def getfilename(obj):
    return obj.split('/')[-1].rsplit(':', 1)[0]

@register.filter
def getfileid(obj):
    return obj.split('/')[-1].rsplit(':', 1)[-1]


@register.filter
def slice_unicode(obj, how_much):
    return obj.decode('utf-8')[:how_much].encode('utf-8')


@register.filter
def friendly_sched_type(type):
    if type == 'Weekly':
        return 'Semanal'
    elif type == 'Monthly':
        return 'Mensal'
