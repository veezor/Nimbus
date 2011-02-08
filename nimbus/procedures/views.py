# -*- coding: utf-8 -*-
# Create your views here.



from time import strftime, strptime

from django.contrib.auth.decorators import login_required
from django.views.generic import create_update
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


from nimbus.bacula.models import Job
from nimbus.procedures.models import Procedure, Profile
from nimbus.computers.models import Computer
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.offsite.models import Offsite

from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form, form_mapping
from nimbus.shared.enums import days as days_enum, weekdays as weekdays_enum, levels as levels_enum
from nimbus.procedures.forms import ProfileForm




@login_required
def add(request):
    extra_context = {'title': u"Adicionar procedimento"}
    return create_update.create_object( request, 
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



@login_required
def edit(request, object_id):
    extra_context = {'title': u"Editar procedimento"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



@login_required
def delete(request, object_id):
    if request.method == "POST":
        procedure = Procedure.objects.get(id=object_id)
        procedure.delete()
        messages.success(request, u"Procedimento removido com sucesso.")
        return redirect('nimbus.procedures.views.list')
    else:
        procedure = Procedure.objects.get(id=object_id)
        remove_name = procedure.name
        return render_to_response(request, 'remove.html', locals())


@login_required
def execute(request, object_id):
    
    procedure = Procedure.objects.get(id=object_id)
    procedure.run()
    messages.success(request, u"Procedimento em execução.")
    return redirect('nimbus.procedures.views.list')




@login_required
def list(request):
    procedures = Procedure.objects.all()

    offsite = Offsite.get_instance()
    offsite_on = offsite.active

    title = u"Procedimentos"
    running_status = ('R','p','j','c','d','s','M','m','s','F','B')
    running_jobs = Job.objects.filter( jobstatus__in=running_status)\
                                            .order_by('-starttime').distinct()[:5]


    last_jobs = Job.objects.all()\
                    .order_by('-endtime').distinct()[:5]

    running_procedures_content = []
    try:
        for job in running_jobs:
            running_procedures_content.append({
                'type' : 'ok',
                'label' : job.procedure.name,
                'date' : job.starttime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


    last_procedures_content = []
    try:
        for job in last_jobs:
            last_procedures_content.append({
                'type' : job.status_friendly,
                'label' : job.procedure.name,
                'date' : job.endtime,
                'message' : u'Computador : %s' % job.client.computer.name
            })
    except (Procedure.DoesNotExist, Computer.DoesNotExist), error:
        pass


    
    procedimentos_em_execucao_executados = [{
        'title': u'Procedimentos em execução',
        'content': running_procedures_content
        }, {
        'title': u'Últimos procedimentos executados',
        'content': last_procedures_content   
        }]
    
    return render_to_response(request, "procedures_list.html", locals())



@login_required
def list_offsite(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos com offsite ativo"
    }
    return render_to_response(request, "procedures_list.html", extra_content)


@login_required
def activate_offsite(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    procedure.offsite_on = True
    procedure.save()
    return redirect('/procedures/list')


@login_required
def deactivate_offsite(request, object_id):
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
    profiles = Profile.objects.all()
    return render_to_response(request, "profile_list.html", locals())


@login_required
def profile_add(request):
    title = u"Adicionar perfil de configuração"
    
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    computers = Computer.objects.all()
    
    days = days_enum
    weekdays = weekdays_enum
    levels = levels_enum
    errors = {}

    if request.method == "GET":
        profile_form = ProfileForm()
        return render_to_response(request, "profile_add.html", locals())
    elif request.method == "POST":
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Perfil de configuração criado com sucesso")
            return redirect('nimbus.procedures.views.profile_list')
        else:
            return render_to_response(request, "profile_add.html", locals())
    else:
        #NOT GET OR POST
        pass
        

        


@login_required
def profile_edit(request, object_id):
    title = u"Editar perfil de configuração"
    profile = Profile.objects.get(id=object_id)
    
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    
    if request.method == "POST":
        
        if request.POST.get('save_as_new'):
            object_id = None

        form = form_mapping(Profile, request.POST, object_id=object_id)

        if form.is_valid():
            profile = form.save()
            messages.success(request,
                u"Perfil de configuração atualizado com sucesso.")
            return redirect('nimbus.procedures.views.profile_list')
    
    return render_to_response(request, "profile_edit.html", locals())


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
