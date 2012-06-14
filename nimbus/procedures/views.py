# -*- coding: utf-8 -*-
# Create your views here.

from copy import copy
from time import strftime, strptime

from django.contrib.auth.decorators import login_required
from django.views.generic import create_update
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.translation import ugettext as _

from pybacula import BConsoleInitError

from nimbus.bacula.models import Job
from nimbus.procedures.models import Procedure, JobTask
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form, form_mapping
from nimbus.libs.bacula import call_reload_baculadir
from nimbus.shared.enums import days as days_enum, weekdays as weekdays_enum, levels as levels_enum
from nimbus.procedures.forms import ProcedureForm, ProcedureEditForm
from nimbus.schedules.models import Schedule


@login_required
def add(request, teste=None):

    initial = {}
    if request.method == "GET":
        computer = request.GET.get("comp_id", 0)

        if computer:
            initial = {"computer" : computer}
        else:
            initial = {}

    title = _(u"Add backup")
    form = ProcedureForm(initial=initial, prefix="procedure")
    tasks = JobTask.objects.all()
    content = {'title': title,
                'form':form,
                'tasks': tasks}
    if request.method == "POST":
        data = copy(request.POST)
        if data["procedure-fileset"]:
            fileset = FileSet.objects.get(id=data['procedure-fileset'])
            content['fileset'] = fileset
        if data["procedure-schedule"]:
            schedule = Schedule.objects.get(id=data['procedure-schedule'])
            content['schedule'] = schedule
        procedure_form = ProcedureForm(data, prefix="procedure")
        if procedure_form.is_valid():
            procedure = procedure_form.save()
            call_reload_baculadir()
            messages.success(request, _("Backup procedure '%s' successfully created") % procedure.name)
            return redirect('/procedures/list')
        else:
            messages.error(request, _("The backup procedure has not been created due to the following errors:"))
            content['form'] = procedure_form
            return render_to_response(request, "add_procedure.html", content)
    return render_to_response(request, "add_procedure.html", content)


@login_required
def edit(request, procedure_id):
    p = get_object_or_404(Procedure, pk=procedure_id)
    title = _(u"Editing '%s'") % p.name
    partial_form = ProcedureForm(prefix="procedure", instance=p)
    content = {'title': title,
              'form': partial_form,
              'id': procedure_id,
              'procedure': p,
              'schedule': p.schedule,
              'fileset': p.fileset,
              'retention_time': p.pool_retention_time}
    if request.method == "POST":
        data = copy(request.POST)
        if data['procedure-schedule'] == u"":
            data['procedure-schedule'] = u"%d" % p.schedule.id
        if data['procedure-fileset'] == u"":
            data['procedure-fileset'] = u"%d" % p.fileset.id
        procedure_form = ProcedureForm(data, instance=p, prefix="procedure")
        if procedure_form.is_valid():
            procedure_form.save()
            messages.success(request, _("Procedure '%s' changed successfully.") % p.name)
            call_reload_baculadir()
            return redirect('/procedures/list')
        else:
            messages.error(request, _("The backup procedure has not been created due to the following errors:"))
            content['forms'] = [procedure_form]
            return render_to_response(request, "edit_procedure.html", content)
    return render_to_response(request, 'edit_procedure.html', content)


@login_required
def delete(request, object_id):
    p = get_object_or_404(Procedure, pk=object_id)
    jobs = p.all_my_jobs
    content = {'procedure': p,
               'last_jobs': jobs}
    return render_to_response(request, "remove_procedure.html", content)


@login_required
def do_delete(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    if not procedure.schedule.is_model:
        procedure.schedule.delete()
    if not procedure.fileset.is_model:
        procedure.fileset.delete()
    procedure.delete()
    call_reload_baculadir()
    messages.success(request, _(u"Procedure successfully removed."))
    return redirect('/procedures/list')


@login_required
def execute(request, object_id):
    try:
        procedure = Procedure.objects.get(id=object_id)
        procedure.run()
        messages.success(request, _(u"Procedure in execution."))
    except BConsoleInitError, error:
        messages.error(request, _(u"Backup server down, impossible to perform the operation."))
    return redirect('/procedures/list')

@login_required
def list_all(request):
    procedures = Procedure.objects.filter(id__gt=1)
    title = _(u"Backup procedure")
    last_jobs = Procedure.all_non_self_jobs()[:10]
    return render_to_response(request, "procedures_list.html", locals())

@login_required
def activate(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.active = True
        procedure.save()
        call_reload_baculadir()
        messages.success(request, _("Procedure successfully activated"))
    return redirect('/procedures/list')

@login_required
def deactivate(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.active = False
        procedure.save()
        call_reload_baculadir()
        messages.success(request, _("Procedure successfully deactivated"))
    return redirect('/procedures/list')

@login_required
def profile_list(request):
    title = _(u"Profiles configuration")
    filesets = FileSet.objects.filter(is_model=True)
    schedules = Schedule.objects.filter(is_model=True)
    computers = Computer.objects.filter(active=True,id__gt=1)
    content = {'title': _(u"Profiles configuration"),
               'filesets': filesets,
               'schedules': schedules,
               'computers': computers}
    return render_to_response(request, "profile_list.html", content)

    
@login_required
def history(request, object_id=False):
    #TODO: Filtrar jobs de um procedimento específico
    title = _(u'Procedural History')
    # get page number
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    #get all jobs
    all_jobs = Procedure.all_non_self_jobs()
    paginator = Paginator(all_jobs, 20)
    try:
        jobs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        jobs = paginator.page(paginator.num_pages)
    last_jobs = jobs.object_list
    return render_to_response(request, "procedures_history.html", locals())



@login_required
def cancel_job(request, job_id):
    if request.method == "POST":
        Procedure.cancel_jobid(job_id)
        messages.success(request, _("Procedure successfully canceled"))
    return redirect('/procedures/list')





















