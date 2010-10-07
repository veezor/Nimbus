# -*- coding: utf-8 -*-
# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from nimbus.procedures.models import Procedure, Profile
from nimbus.storages.models import Storage
from nimbus.schedules.models import Schedule
from nimbus.filesets.models import FileSet
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form

from django.contrib import messages

def add(request):
    extra_context = {'title': u"Adicionar procedimento"}
    return create_update.create_object( request, 
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



def edit(request, object_id):
    extra_context = {'title': u"Editar procedimento"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Procedure,
                                        form_class = form(Procedure),
                                        template_name = "base_procedures.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/procedures/")



def delete(request):
    pass


def execute(request, object_id):
    # executar o procedimento agora.
    messages.success(request, u"Procedimento em execução.")
    return redirect('nimbus.procedures.views.list')


# def view(request, object_id):
#     procedures = Procedure.objects.get(id=object_id)
#     extra_content = {
#         'procedure': procedures,
#         'title': u"Visualizar computador"
#     }
#     return render_to_response(request, "procedures_view.html", extra_content)


def list(request):
    procedures = Procedure.objects.all()
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos"
    }
    return render_to_response(request, "procedures_list.html", extra_content)


def list_offsite(request):
    procedures = Procedure.objects.filter(offsite_on=True)
    extra_content = {
        'procedures': procedures,
        'title': u"Procedimentos com offsite ativo"
    }
    return render_to_response(request, "procedures_list.html", extra_content)


def activate_offsite(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    procedure.offsite_on = True
    procedure.save()
    return redirect('/procedures/list')


def deactivate_offsite(request, object_id):
    procedure = Procedure.objects.get(id=object_id)
    procedure.offsite_on = False
    procedure.save()
    return redirect('/procedures/list')



def profile_list(request):
    title = u"Perfis de configuração"
    profiles = Profile.objects.all()
    return render_to_response(request, "profile_list.html", locals())


def profile_add(request):
    title = u"Adicionar perfil de configuração"
    
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    
    if request.method == "POST":
        # profile_name
        # profile_storage_id
        # profile_schedule_id
        # profile_fileset_id
        print request.POST
        messages.success(request,
            u"Perfil adicionado com sucesso.")
    
    return render_to_response(request, "profile_add.html", locals())


def profile_edit(request, object_id):
    title = u"Editar perfil de configuração"
    profile = Profile.objects.get(id=object_id)
    
    storages = Storage.objects.all()
    schedules = Schedule.objects.all()
    filesets = FileSet.objects.all()
    
    if request.method == "POST":
        # Se vier a variavel save_as_new, deve salvar como novo perfil.
        
        # profile_name
        # profile_storage_id
        # profile_schedule_id
        # profile_fileset_id
        print request.POST
        messages.success(request,
            u"Perfil de configuração atualizado com sucesso.")
    
    return render_to_response(request, "profile_edit.html", locals())
