#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm

from environment import ENV

from backup_corporativo.bkp.utils import redirect, reverse
from backup_corporativo.bkp.models import GlobalConfig, TimezoneConfig, NetworkInterface, Procedure, Wizard, Storage
from backup_corporativo.bkp.forms import NetworkInterfaceEditForm, GlobalConfigForm, TimezoneForm, OffsiteConfigForm, PingForm, TraceRouteForm, NsLookupForm
from backup_corporativo.bkp.views import global_vars, authentication_required

from keymanager import KeyManager
from backup_corporativo.bkp.forms import NewStrongBoxForm, WizardGlobalConfigForm, WizardTimezoneConfigForm, WizardNetworkForm

# Controle de passos do wizard
# Para adicionar um passo ao wizard basta seguir esses 3 passos:
#   1) declarar rotas no urls.py
#   2) declarar views no app_views/wizard.py
#     - p.s.: nas views, após fazer o que deseja, avance um passo utilizando
#             "__advance_step(wizard)" e redirecione para "__next_view(wizard)". 
#             Isso vai conectar a saída da sua view, com o resto do wizard. 
#   3) adicionar nomes das views em WIZARD_STEPS na ordem desejada
# Nota: a última entrada da lista, será o local para onde o usuário
#       será redirecionado após o término do wizard.
WIZARD_STEPS = [ 'edit_wizard_network',
                 'edit_wizard_config', 
                 'edit_wizard_timezone',
                 'edit_wizard_strongbox', ]
WIZARD_EXIT = 'main_management' 

def __next_view(wizard):
    """ Retorna o nome da view de acordo com wizard.step atual.
        Deve ser utilizado pela view para redirecionar de um
        passo do wizard para o outro passo.
    """
    # TODO: verificar exceção de wizard_step inválido
    return WIZARD_STEPS[wizard.wizard_step]

def __final_step_index():
    """ Calcula o número relativo ao último passo que é
        possível atingir nesse wizard. Levar em consideração
        esse número, garante que o wizard não atinja um
        passo inválido.
    """
    return WIZARD_STEPS.__len__() - 1

def __advance_step(wizard):
    """ Incrementa a variável de passo atual. 
        Deve ser utilizada sempre antes de passar de um passo
        do wizard para outro.
        O passo só será atualizado caso não seja o último passo.
        Neste caso, o wizard permanecerá sem alterações.
    """
    if wizard.wizard_step < __final_step_index():
        wizard.wizard_step += 1
        wizard.save()

def __reset_step(current_view):
    """ Reseta passo para o passo correspondente
        a current_view pasada no argumento
    """
    if current_view in WIZARD_STEPS:
        wizard = Wizard.get_instance()
        wizard.wizard_step = WIZARD_STEPS.index(current_view)
        wizard.save()


@authentication_required
def main_wizard(request):
    E = ENV(request)

    if request.method == 'GET':
        wizard = Wizard.get_instance()
        if not wizard.wizard_lock:
            # Somente avance
            location = reverse(__next_view(wizard))
        else:
            E.msg = u"Seu sistema já foi configurado!"
            location = reverse(WIZARD_EXIT)
        return HttpResponseRedirect(location)


@authentication_required
def edit_wizard_config(request):
    E = ENV(request)

    if request.method == 'GET':
        wizard = Wizard.get_instance()
        __reset_step('edit_wizard_config')
        E.gconfigform = WizardGlobalConfigForm(instance=wizard)
        
        E.template = 'bkp/wizard/obe/edit_wizard_config.html'
        return E.render()
    

@authentication_required
def update_wizard_config(request):
   E = ENV(request)

   if request.method == 'POST':
       wizard = Wizard.get_instance()
       E.gconfigform = WizardGlobalConfigForm(request.POST, instance=wizard)
       if E.gconfigform.is_valid():
           wizard = E.gconfigform.save()
           __advance_step(wizard)
           location = reverse(__next_view(wizard)) 
           return HttpResponseRedirect(location)
       else:
           E.template = 'bkp/wizard/obe/edit_wizard_config.html'
           return E.render()


@authentication_required
def edit_wizard_network(request):
    E = ENV(request)
    
    if request.method == 'GET':
        wizard = Wizard.get_instance()
        __reset_step('edit_wizard_network')
        wizard.set_network_defaults()
        E.iface_form = WizardNetworkForm(instance=wizard)

        E.template = 'bkp/wizard/obe/edit_wizard_network.html'
        return E.render()


@authentication_required
def update_wizard_network(request):
   E = ENV(request)

   if request.method == 'POST':
       wizard = Wizard.get_instance()
       E.iface_form = WizardNetworkForm(request.POST, instance=wizard)
       if E.iface_form.is_valid():
           wizard = E.iface_form.save()
           __advance_step(wizard)
           location = reverse(__next_view(wizard))
           return HttpResponseRedirect(location)
       else:
           E.template = 'bkp/wizard/obe/edit_wizard_network.html'
           return E.render()

@authentication_required
def edit_wizard_timezone(request):
    E = ENV(request)

    if request.method == 'GET':
        wizard = Wizard.get_instance()
        __reset_step('edit_wizard_timezone')
        E.tconfigform = WizardTimezoneConfigForm(instance=wizard)
        if TimezoneConfig.timezone_configured():
            E.tconfigform.load_area_choices(wizard.tz_country)
        E.template = 'bkp/wizard/obe/edit_wizard_timezone.html'
        return E.render()
    

@authentication_required
def update_wizard_timezone(request):
   E = ENV(request)

   if request.method == 'POST':
       tz_country = request.POST.get('tz_country', [])
       wizard = Wizard.get_instance()
       E.tconfigform = WizardTimezoneConfigForm(request.POST, instance=wizard)
       E.tconfigform.load_area_choices(tz_country)
       if E.tconfigform.is_valid():
           wizard = E.tconfigform.save()
           __advance_step(wizard)
           location = reverse(__next_view(wizard)) 
           return HttpResponseRedirect(location)
       else:
           E.template = 'bkp/wizard/obe/edit_wizard_timezone.html'
           return E.render()

@authentication_required
def edit_wizard_strongbox(request):
    E = ENV(request)    

    if request.method == 'GET':
        wizard = Wizard.get_instance()
        __reset_step('edit_wizard_strongbox')
        E.gconfig = wizard.global_config
        E.iface = wizard.network_interface
        E.tconfig = E.wizard.timezone_config
        E.sbox_form = NewStrongBoxForm()
        
        E.template = 'bkp/wizard/obe/edit_wizard_strongbox.html'
        return E.render()
    

@authentication_required
def update_wizard_strongbox(request):
   E = ENV(request)
   
   if request.method == 'POST':
       E.wizard = Wizard.get_instance()

       E.gconfig = E.wizard.global_config
       E.iface = E.wizard.network_interface
       E.tconfig = E.wizard.timezone_config


       # Validar criação da Interface de Rede
       iface = E.wizard.network_interface_querydict() # request.POST
       iface_form = NetworkInterfaceEditForm(iface) # simulando request.POST
       if iface_form.is_valid():
           iface_form.save()
       else:
           E.msg = "Existem erros com a configuração de rede."
           location = reverse('edit_wizard_network')
           return HttpResponseRedirect(location)
 

       # Validar criação da Configuração Global
       gconf = E.wizard.global_config_querydict() # request.POST
       gconfigform = GlobalConfigForm(gconf) # simulando request.POST
       if gconfigform.is_valid():
           gconfigform.save()
       else:
           E.msg = "Existem erros com a configuração global."
           location = reverse('edit_wizard_config')
           return HttpResponseRedirect(location)
       
      
       # Validar criação da Configuração Timezone
       tconf = E.wizard.timezone_config_querydict() # request.POST
       tconfigform = TimezoneForm(tconf) # simulando request.POST
#       tz_country = request.POST.get('tz_country', [])
       tz_country = tconf.get('tz_country', [])
       tconfigform.load_area_choices(tz_country)
       if tconfigform.is_valid():
           tconfigform.save()
       else:
           E.msg = "Existem erros com a configuração timezone."
           location = reverse('edit_wizard_timezone')
           return HttpResponseRedirect(location)
           
       E.sbox_form = NewStrongBoxForm(request.POST)
       # Validar criação do Cofre
       if E.sbox_form.is_valid():
           pass
       else:
           E.msg = 'Existem erros com a senha do cofre'
           E.template = 'bkp/wizard/obe/edit_wizard_strongbox.html'
           return E.render()

       # Finalizando wizard
       E.wizard.set_wizard_lock(True) # falta implementar
       E.msg = u"Seu sistema foi configurado com sucesso!"
       location = reverse(WIZARD_EXIT)
       return HttpResponseRedirect(location)
