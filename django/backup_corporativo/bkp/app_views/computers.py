#!/usr/bin/python
# -*- coding: utf-8 -*-


import xmlrpclib


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from environment import ENV
from keymanager import KeyManager

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Computer, Encryption
from backup_corporativo.bkp.forms import ComputerForm, ProcedureForm, FileSetForm, WizardAuxForm, MountStrongBoxForm
from backup_corporativo.bkp.views import authentication_required, DAYS_OF_THE_WEEK
from backup_corporativo.bkp.app_models.computer import UnableToGetFile


CLIENT_PORT = 17800 


@authentication_required
def new_computer(request):
    E = ENV(request)

    if request.method == 'GET':
        km = KeyManager()
        if not km.has_drive():
            E.msg = u'Para criar um computador é necessário haver um cofre'
            location = reverse("new_strongbox")
            return HttpResponseRedirect(location)
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        if Computer.objects.count() > 14:
            E.msg = u"Erro ao adicionar computador: limite de computadores foi atingido."
            location = reverse('list_computers')
            return HttpResponseRedirect(location)
        E.mounted = km.mounted
        if not E.mounted:
            E.mountform = MountStrongBoxForm()
        E.compform = ComputerForm(request.GET)
        E.template = 'bkp/computer/new_computer.html'
        return E.render()


@authentication_required
def create_computer(request):
    E = ENV(request)

    if request.method == 'POST':
        km = KeyManager()
        E.mountform = MountStrongBoxForm(request.POST)
        E.compform = ComputerForm(request.POST, instance=Computer())
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            E.wizard = E.wizauxform.cleaned_data['wizard']
        # Apenas por segurança
        else:
            E.wizard = False
        if Computer.objects.count() > 14:
            E.msg = u"Erro ao adicionar computador: limite de computadores foi atingido."
            location = reverse('list_computers')
            return HttpResponseRedirect(location)
        if E.compform.is_valid():
            if not km.mounted:
                if E.mountform.is_valid():
                    pass
                else:
                    E.template = 'bkp/computer/new_computer.html'
                    return E.render()                

            
            comp = E.compform.save()
            enc = Encryption()
            enc.computer = comp
            enc.save()

            try:
                configure_client(comp)
            except Exception, error:
                E.comp = comp
                E.template = 'bkp/computer/new_computer_error.html'
                return E.render()


            location = reverse('new_computer_backup', [comp.id])
            location += "?wizard=%s" % E.wizard
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/computer/new_computer.html'
            return E.render()




def configure_client(computer):
    url = "http://%s:%d" % (computer.computer_ip, CLIENT_PORT)
    proxy = xmlrpclib.ServerProxy(url)
    proxy.save_baculafd(computer.get_config_file())
    proxy.save_private_key(computer.get_crypt_file("key"))
    proxy.restart_bacula()


@authentication_required
def configure_computer(request, comp_id):
    if request.method == "GET":
        E = ENV(request)
        comp = Computer.objects.get(id=comp_id)
        try:
            configure_client(comp)
        except Exception, error:
            print error
            E.comp = comp
            E.template = 'bkp/computer/new_computer_error.html'
            return E.render()
        
        location = reverse('new_computer_backup', [comp_id])
        location += "?wizard=%s" % E.wizard
        return HttpResponseRedirect(location)




@authentication_required
def edit_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(instance=E.comp)
        E.template = 'bkp/computer/edit_computer.html',
        return E.render()


@authentication_required
def update_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.comp = get_object_or_404(Computer, pk=comp_id)
        E.compform = ComputerForm(request.POST,instance=E.comp)
        if E.compform.is_valid():
            E.compform.save()
            E.msg = u"Computador foi alterado com sucesso."
            location = reverse('view_computer', args=[comp_id])
            return HttpResponseRedirect(location)
        else:
            E.msg = u"Erro ao alterar computador."
            E.template = 'bkp/computer/edit_computer.html'
            return E.render()


@authentication_required
def view_computer(request, comp_id):
    E = ENV(request)

    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        unsuccessful_jobs = E.comp.unsuccessful_jobs()
        paginator = Paginator(unsuccessful_jobs, 15)
        # Eta paginador ruinzin...
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            E.unsuccessful_jobs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            E.unsuccessful_jobs = paginator.page(paginator.num_pages)

        E.procs = E.comp.procedure_set.all()
        E.running_jobs = E.comp.running_jobs()
        E.successful_jobs = E.comp.successful_jobs()
        E.compstatus = E.comp.get_status()
        E.DAYS_OF_THE_WEEK = DAYS_OF_THE_WEEK
        
        E.template = 'bkp/computer/view_computer.html'
        return E.render()


@authentication_required
def delete_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.comp = get_object_or_404(Computer,pk=comp_id)
        E.template = 'bkp/computer/delete_computer.html'
        return E.render()
    elif request.method == 'POST':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.delete()
        E.msg = u"Computador foi removido permanentemente."
        return HttpResponseRedirect(reverse("list_computers"))


@authentication_required
def test_computer(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        comp = get_object_or_404(Computer,pk=comp_id)
        comp.run_test_job()
        E.msg = u"Uma requisiçao foi enviada ao computador."
        location = reverse("view_computer", args=[comp_id])
        return HttpResponseRedirect(location)


@authentication_required
def view_computer_config(request, comp_id):
    E = ENV(request)
    km = KeyManager()
    E.has_drive = km.has_drive()
    E.mounted = km.mounted
    
    
    if request.method == 'GET':
        E.comp = Computer.objects.get(pk=comp_id)
        E.comp_config = E.comp.get_config_file()
        E.template = 'bkp/computer/view_computer_config.html'
        return E.render()


@authentication_required
def dump_computer_file(request, comp_id):
    km = KeyManager()
    if request.method == 'POST':
        E = ENV(request)
        computer = Computer.objects.get(pk=comp_id)
        if 'file_type' in request.POST:
            file_type = request.POST['file_type']
        else:
            file_type = None 
        
        # Caso seja um arquivo de criptografia, o cofre precisa estar aberto
        # senão usuário será redirecionado de volta para view_computer
        if (file_type in ('key', 'certificate', 'pem') and (not km.mounted)):
            E.msg = 'É necessário abrir o cofre.'
            location = reverse('view_computer_config', args=[computer.id])
            return HttpResponseRedirect(location)
        try:
            file_content = computer.get_file(file_type)
        except UnableToGetFile:
            E.msg = 'Erro ao baixar chave, por favor entre em contato com o suporte.'
            location = reverse('view_computer_config',args=[computer.id])
            return HttpResponseRedirect(location)
        file_name = Computer.FILE_NAMES[file_type]
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response.write(file_content)
        return response


@authentication_required
def new_computer_backup(request, comp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        if 'wizard' in request.GET:
            E.wizard = request.GET['wizard']
        else:
            E.wizard = False
        E.comp = get_object_or_404(Computer, pk=comp_id)            
        E.procform = ProcedureForm()
        E.fsetform = FileSetForm()    
        E.template = 'bkp/computer/new_computer_backup.html'
        return E.render()


@authentication_required
def create_computer_backup(request, comp_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.wizauxform = WizardAuxForm(request.POST)
        if E.wizauxform.is_valid():
            wiz = E.wizauxform.cleaned_data['wizard']
        # Apenas por segurança
        else:
            wiz = False
        E.comp = get_object_or_404(Computer, pk=comp_id)            
        E.procform = ProcedureForm(request.POST)
        E.fsetform = FileSetForm(request.POST)
        forms_list = [E.procform, E.fsetform]
        if all([form.is_valid() for form in forms_list]):
            proc = E.procform.save(commit=False)
            fset = E.fsetform.save(commit=False)
            proc.computer_id = comp_id
            proc.save()
            fset.procedure_id = proc.id
            fset.save()
            location = reverse("new_procedure_schedule", args=[proc.id])
            location += "?wizard=%s" % wiz
            return HttpResponseRedirect(location)
        else:
            E.wizard = wiz
            E.template = 'bkp/computer/new_computer_backup.html'
            return E.render()
