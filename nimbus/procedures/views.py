# -*- coding: utf-8 -*-
# Create your views here.

from copy import copy
from time import strftime, strptime

from django.contrib.auth.decorators import login_required
from django.views.generic import create_update
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from pybacula import BConsoleInitError

from nimbus.bacula.models import Job
from nimbus.procedures.models import Procedure
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.offsite.models import Offsite
#from nimbus.pools.models import Pool
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form, form_mapping
from nimbus.shared.enums import days as days_enum, weekdays as weekdays_enum, levels as levels_enum
from nimbus.procedures.forms import ProcedureForm, ProcedureEditForm
from nimbus.schedules.models import Schedule


@login_required
def add(request, teste=None):
    comp_id = 0
    if request.GET:
        comp_id = request.GET["comp_id"]
    title = u"Adicionar backup"
    form = ProcedureForm(prefix="procedure")
    #print "form"*10
    #print form
    schedule_return = False
    fileset_return = False
    content = {'title': title,
                'schedule_return': schedule_return,
                'fileset_return': fileset_return,
                'form':form,
                'init_script': "",
                'comp_id': comp_id}
    if request.method == "POST":
        data = copy(request.POST)
        print "data"*10
        print data
        # retorna o ajax caso haja submissão do formulário
        if data['schedule_return']:
            content['init_script'] = "$(field_schedule).val(%s);set_schedule();" % data['schedule_return']
        if data['fileset_return']:
            content['init_script'] += "$(field_fileset).val(%s);set_fileset();" % data['fileset_return']
        print data["procedure-fileset"]
        if data["procedure-fileset"]:
            fileset = FileSet.objects.get(id=data['procedure-fileset'])
            content['fileset'] = fileset
        procedure_form = ProcedureForm(data, prefix="procedure")
        if len(data['procedure-pool_retention_time']) > 4:
            messages.error(request, "O tempo de retenção é muito alto, por favor escolha um valor menor")
            content['form'] = procedure_form
            return render_to_response(request, "add_procedure.html", content)
        elif procedure_form.is_valid():
            procedure = procedure_form.save()
            messages.success(request, "Procedimento de backup '%s' criado com sucesso" % procedure.name)
            return redirect('/procedures/list')
        else:
            messages.error(request, "O procedimento de backup não foi criado devido aos seguintes erros")
            content['form'] = procedure_form
            return render_to_response(request, "add_procedure.html", content)
    return render_to_response(request, "add_procedure.html", content)


@login_required
def edit(request, procedure_id):
    p = get_object_or_404(Procedure, pk=procedure_id)
    title = u"Editando '%s'" % p.name
    partial_form = ProcedureForm(prefix="procedure", instance=p)
    lforms = [partial_form]
    content = {'title': title,
              'forms':lforms,
              'id': procedure_id,
              'procedure': p,
              'schedule': p.schedule,
              'fileset': p.fileset}
    if request.method == "POST":
        data = copy(request.POST)
        if data['procedure-schedule'] == u"":
            data['procedure-schedule'] = u"%d" % p.schedule.id
        if data['procedure-fileset'] == u"":
            data['procedure-fileset'] = u"%d" % p.fileset.id
        procedure_form = ProcedureForm(data, instance=p, prefix="procedure")
        if procedure_form.is_valid():
            procedure_form.save()
            messages.success(request, "Procedimento '%s' alterado com sucesso" % p.name)
            return redirect('/procedures/list')
        else:
            messages.error(request, "O procedimento de backup não foi criado devido aos seguintes erros")
            content['forms'] = [procedure_form]
            return render_to_response(request, "edit_procedure.html", content)
    return render_to_response(request, 'edit_procedure.html', content)


@login_required
def delete(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        if not procedure.schedule.is_model:
            procedure.schedule.delete()
        if not procedure.fileset.is_model:
            procedure.fileset.delete()
        procedure.delete()
        messages.success(request, u"Procedimento removido com sucesso.")
        return redirect('/procedures/list')
    else:
        procedure = Procedure.objects.get(id=object_id)
        remove_name = procedure.name
        return render_to_response(request, 'remove.html', locals())

@login_required
def execute(request, object_id):
    try:
        procedure = Procedure.objects.get(id=object_id)
        procedure.run()
        messages.success(request, u"Procedimento em execução.")
    except BConsoleInitError, error:
        messages.error(request, u"Servidor de backup inativo, impossível realizar operação.")
    return redirect('/procedures/list')

@login_required
def list_all(request):
    procedures = Procedure.objects.filter(id__gt=1)
    offsite = Offsite.get_instance()
    offsite_on = offsite.active
    title = u"Procedimentos de backup"
    last_jobs = Procedure.all_jobs()[:10]
    return render_to_response(request, "procedures_list.html", locals())

@login_required
def list_offsite(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {'procedures': procedures,
                     'title': u"Procedimentos com offsite ativo"}
    return render_to_response(request, "procedures_list.html", extra_content)

@login_required
def activate_offsite(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.offsite_on = True
        procedure.save()
    return redirect('/procedures/list')

@login_required
def deactivate_offsite(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.offsite_on = False
        procedure.save()
    return redirect('/procedures/list')

@login_required
def activate(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.active = True
        procedure.save()
        messages.success(request, "Procedimento ativado com sucesso")
    return redirect('/procedures/list')

@login_required
def deactivate(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.active = False
        procedure.save()
        messages.success(request, "Procedimento desativado com sucesso")
    return redirect('/procedures/list')

@login_required
def profile_list(request):
    title = u"Perfis de configuração"
    filesets = FileSet.objects.filter(is_model=True)
    schedules = Schedule.objects.filter(is_model=True)
    computers = Computer.objects.all()
    content = {'title': u"Perfis de configuração",
               'filesets': filesets,
               'schedules': schedules,
               'computers': computers}
    return render_to_response(request, "profile_list.html", content)

@login_required
def profile_delete(request, object_id):
    profile = get_object_or_404(Profile, pk=object_id)
    if request.method == "POST":
        n_procedures = Procedure.objects.filter(profile=profile).count()
        if n_procedures:
            messages.error(request, u"Impossível remover perfil em uso")
        else:
            profile.delete()
            messages.success(request, u"Procedimento removido com sucesso.")
            return redirect('nimbus.procedures.views.profile_list')
    remove_name = profile.name
    return render_to_response(request, 'remove.html', locals())
    
@login_required
def history(request, object_id=False):
    #TODO: Filtrar jobs de um procedimento específico
    title = u'Histórico de Procedimentos'
    # get page number
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    #get all jobs
    all_jobs = Procedure.all_jobs()
    paginator = Paginator(all_jobs, 5)
    try:
        jobs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        jobs = paginator.page(paginator.num_pages)
    last_jobs = jobs.object_list
    return render_to_response(request, "procedures_history.html", locals())























