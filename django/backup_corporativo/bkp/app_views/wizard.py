#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from os import path

from django.http import HttpResponseRedirect
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings

from environment import ENV

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import ( GlobalConfig, 
                                            TimezoneConfig, 
                                            NetworkInterface, 
                                            Wizard, 
                                            Storage,
                                            Device )

from backup_corporativo.bkp.forms import ( NetworkInterfaceEditForm, 
                                           GlobalConfigForm, 
                                           TimezoneForm, 
                                           NewStrongBoxForm )



from backup_corporativo.bkp.views import authentication_required



def update_empty_jobs(storage):
    filename = path.join( settings.NIMBUS_CUSTOM_PATH, 
                          "jobs", "default")

    f = file(filename)
    content = f.read()
    f.close()

    f = file(filename, "w")
    f.write( content.replace("StorageLocal",storage.storage_bacula_name()))
    f.close()



class WizardStateMachine(object):

    states = [ 'edit_wizard_network',
               'edit_wizard_config', 
               'edit_wizard_timezone',
               'edit_wizard_strongbox',
               'confirm_wizard']

    def __init__(self):
        self.wizard = Wizard.get_instance()

    @property
    def state(self):
        return self.states[ self.wizard.state ]

    def go_next_state(self):
        s = self.wizard.state + 1
        if s < len(self.states):
            self.wizard.state = s
            self.wizard.save()
            return self.go_current_state()

    def go_current_state(self):
        return HttpResponseRedirect(reverse(self.state))

    @property
    def ended(self):
        return self.wizard.completed




@authentication_required
def main_wizard(request):
    E = ENV(request)

    if request.method == 'GET':
        machine = WizardStateMachine() 
        if machine.ended:
            E.msg = u"Seu sistema já foi configurado!"
            return HttpResponseRedirect( reverse("main_statistics") )
        else:
            return machine.go_current_state()


@authentication_required
def edit_wizard_config(request):
    E = ENV(request)

    if request.method == 'GET':
        machine = WizardStateMachine()
        wizard = machine.wizard

        E.gconfigform = GlobalConfigForm(instance=wizard.config)
        E.template = 'bkp/wizard/obe/edit_wizard_config.html'
        return E.render()


@authentication_required
def update_wizard_config(request):
    E = ENV(request)

    if request.method == 'POST':

        machine = WizardStateMachine()
        wizard = machine.wizard
        reedit = wizard.config

        E.gconfigform = GlobalConfigForm(request.POST)

        if E.gconfigform.is_valid():



            storage = Storage(id=1,
                              storage_name="StorageLocal",
                              storage_port=E.gconfigform.cleaned_data['storage_port'],
                              storage_description="Storage local")
            storage.save()
            update_empty_jobs(storage)

            device = Device(id=1,
                            name="Primary device",
                            archive="/var/bacula/archive",
                            storage=storage)
            device.save()


            wizard.config = E.gconfigform.save()
            wizard.save()
            if reedit:
                return machine.go_current_state()
            return machine.go_next_state()
        else:
            E.template = 'bkp/wizard/obe/edit_wizard_config.html'
            return E.render()


@authentication_required
def edit_wizard_network(request):
    E = ENV(request)
    if request.method == 'GET':
        machine = WizardStateMachine()
        wizard = machine.wizard

        if not wizard.network:
            wizard.set_network_defaults()


        E.iface_form = NetworkInterfaceEditForm(instance=wizard.network)
        E.template = 'bkp/wizard/obe/edit_wizard_network.html'
        return E.render()


@authentication_required
def update_wizard_network(request):
    E = ENV(request)
    if request.method == 'POST':

        machine = WizardStateMachine()
        wizard = machine.wizard
        reedit = wizard.network


        E.iface_form = NetworkInterfaceEditForm(request.POST)
        if E.iface_form.is_valid():
            network = E.iface_form.save()
            wizard.network = network
            wizard.save()
            if reedit:
                return machine.go_current_state()
            return machine.go_next_state()
        else:
            E.template = 'bkp/wizard/obe/edit_wizard_network.html'
            return E.render()


@authentication_required
def edit_wizard_timezone(request):
    E = ENV(request)

    if request.method == 'GET':
        machine = WizardStateMachine()
        wizard = machine.wizard

        E.tconfigform = TimezoneForm(instance=wizard.timezone)

        if TimezoneConfig.timezone_configured():
            E.tconfigform.load_area_choices(wizard.timezone.tz_country)

        E.template = 'bkp/wizard/obe/edit_wizard_timezone.html'
        return E.render()


@authentication_required
def update_wizard_timezone(request):
    E = ENV(request)

    if request.method == 'POST':
        tz_country = request.POST.get('tz_country', [])

        machine = WizardStateMachine()
        wizard = machine.wizard
        reedit = wizard.timezone

        wizard.timezone = TimezoneConfig()

        E.tconfigform = TimezoneForm(request.POST)
        E.tconfigform.load_area_choices(tz_country)
        if E.tconfigform.is_valid():
            wizard.timezone = E.tconfigform.save()
            wizard.save()
            if reedit:
                return machine.go_current_state()
            return machine.go_next_state()
        else:
            E.template = 'bkp/wizard/obe/edit_wizard_timezone.html'
            return E.render()



@authentication_required
def edit_wizard_strongbox(request):
    E = ENV(request)    

    if request.method == 'GET':
        E.sbox_form = NewStrongBoxForm()
        E.template = 'bkp/wizard/obe/edit_wizard_strongbox.html'
        return E.render()


@authentication_required
def update_wizard_strongbox(request):
    E = ENV(request)

    if request.method == 'POST':

        E.wizard = Wizard.get_instance()
        E.sbox_form = NewStrongBoxForm(request.POST)

        if not E.sbox_form.is_valid():
            E.msg = 'Existem erros com a senha do cofre'
            E.template = 'bkp/wizard/obe/edit_wizard_strongbox.html'
            return E.render()
        else:
            machine = WizardStateMachine()
            return machine.go_next_state()


@authentication_required
def confirm_wizard(request):
    E = ENV(request)

    wizard = Wizard.get_instance()

    if request.method == 'POST':
        wizard.finish()
        E.msg = u"Seu sistema foi configurado com sucesso!"
        return HttpResponseRedirect(reverse('main_wizard'))
    elif request.method == 'GET':
        E.iface = wizard.network
        E.tconfig = wizard.timezone
        E.gconfig = wizard.config
        E.template = 'bkp/wizard/obe/confirm_wizard.html'
        return E.render()
    else:
        pass
