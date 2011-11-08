# Create your views here.
# -*- coding: UTF-8 -*-

import traceback
import simplejson
import socket
from copy import copy

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib import messages

from nimbus.libs.bacula import call_reload_baculadir
from nimbus.computers.models import Computer
from nimbus.schedules import forms
# from nimbus.shared.enums import levels, days_range, weekdays_range, end_days_range
from nimbus.shared.views import render_to_response
from nimbus.schedules.models import Schedule, BackupLevel, Run, BackupKind
from nimbus.procedures.models import Procedure
from nimbus.shared import utils

@login_required
def add(request):
    referer = utils.Referer(request)
    levels = BackupLevel.objects.all()
    content = {'levels': levels}
    if referer.local == '/procedures/profile/list/':
        content['is_model'] = True
        content['reload'] = True
    else:
        content['reload'] = False
    return render_to_response(request, "add_schedule.html", content)


@login_required
def do_add(request):
    if request.method == 'POST':
        data = request.POST

        if data.has_key('main'):
            new = Schedule()
            new.name = data['name']
            if data['is_model'] == 'true':
                new.is_model = True
            new.save()
            return HttpResponse('{"status": "ok", "new_id": %s}' % new.id)
        elif data.has_key('schedule_id'):
            s = get_object_or_404(Schedule, pk=int(data['schedule_id']))
            try:
                run = Run()
                run.schedule = s
                run.level = BackupLevel.objects.get(id=int(data['level_id']))
                run.kind = BackupKind.objects.get(id=int(data['kind_id']))
                run.hour = data['hour']
                run.minute = data['minute']
                run.day = int(data['day_num'])
                run.save()
                return HttpResponse('{"status": "ok"}')
            except:
                s.delete()
                return HttpResponse('{"status": "error"}')

@login_required
def edit(request, object_id):
    referer = utils.Referer(request)    
    s = get_object_or_404(Schedule, pk=object_id)
    levels = BackupLevel.objects.all()
    content = {'levels': levels,
               'schedule': s,
               'runs': s.runs.all()}
    if referer.local == '/procedures/profile/list/':
        content['is_model'] = True
        content['reload'] = True
    elif referer.local.startswith('/procedures'):
        content['reload'] = False
    return render_to_response(request, "edit_schedule.html", content)

@login_required
def do_edit(request):
    if request.method == 'POST':
        data = request.POST
        if data.has_key('main'):
            s = get_object_or_404(Schedule, pk=int(data['id']))
            s.name = data['name']
            s.save()
            return HttpResponse('{"status": "ok", "new_id": %s}' % s.id)
        elif data.has_key('schedule_id'):
            s = get_object_or_404(Schedule, pk=int(data['schedule_id']))        
            if data['status'] == 'deleted':
                r = get_object_or_404(Run, pk=int(data['id']))
                r.delete()
            try:
                if data['status'] == 'new':
                    run = Run()
                    run.schedule = s
                    run.level = BackupLevel.objects.get(id=int(data['level_id']))
                    run.kind = BackupKind.objects.get(id=int(data['kind_id']))
                    run.hour = data['hour']
                    run.minute = data['minute']
                    run.day = int(data['day_num'])
                    run.save()
                
                call_reload_baculadir()
                return HttpResponse('{"status": "ok"}')
            except:
                return HttpResponse('{"status": "error"}')


@login_required
def delete(request, schedule_id):
    s = get_object_or_404(Schedule, pk=schedule_id)
    procedures = s.procedures.all()
    content = {'schedule': s,
               'procedures': procedures}
    return render_to_response(request, "remove_schedule.html", content)


@login_required
def do_delete(request, schedule_id):
    s = get_object_or_404(Schedule, pk=schedule_id)
    if s.is_model:
        for procedure in s.procedures.all():
            new_schedule = Schedule()
            new_schedule.name = 'Agendamentos de %s' % procedure.name
            new_schedule.is_model = False
            new_schedule.save()
            for run in s.runs.all():
                new_run = Run()
                new_run.schedule = new_schedule
                new_run.level = run.level
                new_run.kind = run.kind
                new_run.day = run.day
                new_run.hour = run.hour
                new_run.minute = run.minute
                new_run.save()
            procedure.schedule = new_schedule
            procedure.save()
    name = s.name
    s.delete()
    call_reload_baculadir()
    messages.success(request, u"Perfil de agendamento '%s' removido com sucesso." % name)
    return redirect('/procedures/profile/list')


@login_required
def reckless_discard(request):
    if request.method == 'POST':
        schedule_id = request.POST["schedule_id"]
        s = get_object_or_404(Schedule, pk=schedule_id)
        # not so reckless
        if not s.procedures.all():
            s.delete()
        # else:
            # leave it to garbage colletor
    return HttpResponse("")
