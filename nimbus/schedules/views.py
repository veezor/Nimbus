# -*- coding: utf-8 -*-

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect

from nimbus.schedules.models import Schedule
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form

from django.contrib import messages
from django.template import RequestContext

from nimbus.shared.enums import days, weekdays, levels, operating_systems

def edit(request, object_id):
    if request.method == "POST":
        # import pdb; pdb.set_trace()
        
        ### Campos que serão recebidos nesta função:
        
        # procedure_name - str
        # computer_id - int
        # profile_id - int
        # 
        # profile.storage_id - int
        # profile.schedule_id - int
        # profile.fileset_id - int
        # 
        # schedule.name - str
        # 
        # schedule.monthly.active - bool
        # schedule.monthly.day - list
        # schedule.monthly.hour - str
        # schedule.monthly.level - int
        # 
        # schedule.weekly.active - bool
        # schedule.weekly.day - list
        # schedule.weekly.hour - str
        # schedule.weekly.level - int
        # 
        # schedule.dayly.active - bool
        # schedule.dayly.day - list
        # schedule.dayly.hour - str
        # schedule.dayly.level - int
        # 
        # schedule.hourly.active - bool
        # schedule.hourly.day - list
        # schedule.hourly.hour - str
        # schedule.hourly.level - int
        
        ## Exemplo do objeto.
        # {
        # u'schedule.monthly.level': [u'Full'],
        # u'procedure_name': [u'asdasdas'],
        # u'schedule.dayly.level': [u'Full'],
        # u'profile.schedule_id': [u'Criar novo agendamento'],
        # u'schedule.weekly.active': [u'1'],
        # u'schedule.dayly.hour': [u''],
        # u'computer_id': [u'1'],
        # u'schedule.weekly.level': [u'Full'],
        # u'profile_id': [u''],
        # u'profile.fileset_id': [u'2'],
        # u'schedule.hourly.minute': [u''],
        # u'fileset_name': [u'', u'', u''],
        # u'schedule.monthly.hour': [u'13:00'],
        # u'profile.storage_id': [u'1'],
        # u'schedule.weekly.day[]': [u'mon', u'wed'],
        # u'schedule.hourly.level': [u'Full'],
        # u'schedule.weekly.hour': [u'21:00'],
        # u'schedule.monthly.day[]': [u'1', u'17', u'29'],
        # u'schedule.monthly.active': [u'1']
        # }
        print request.POST
        # TODO: Adicionar a validação do formulário.
        messages.success(request, u"Agendamento atualizado com sucesso.")

    title = u"Editar agendamento"
    schedule = Schedule.objects.get(id=object_id)
    
    # import pdb; pdb.set_trace()
    
    extra_content = {
        'days': days,
        'weekdays': weekdays,
        'levels': levels,
        'operating_systems': operating_systems,
    }
    extra_content.update(**locals());
    
    return render_to_response(request, 'base_schedules.html', extra_content)

