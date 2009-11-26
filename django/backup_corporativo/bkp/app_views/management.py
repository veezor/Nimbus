#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from environment import ENV
from keymanager import KeyManager

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Storage, HeaderBkp, Encryption
from backup_corporativo.bkp.forms import NewStrongBoxForm, MountStrongBoxForm, HeaderBkpForm, EditHeaderBkpForm, UmountStrongBoxForm, RestoreHeaderBkpForm, ChangePwdStrongBoxForm, EncryptionForm
from backup_corporativo.bkp.views import global_vars, authentication_required

@authentication_required
def list_encryptions(request):
    E = ENV(request)

    if request.method == 'GET':
        E.enc_list = Encryption.objects.all()
        E.template = 'bkp/management/list_encryptions.html'
        return E.render()


@authentication_required
def new_encryption(request):
    E = ENV(request)

    if request.method == 'GET':
        km = KeyManager()
        E.mounted = km.mounted
        if not E.mounted:
            E.mountform = MountStrongBoxForm()
        E.encform = EncryptionForm()
        E.template = 'bkp/management/new_encryption.html'
        return E.render()


@authentication_required
def create_encryption(request):
    E = ENV(request)

    if request.method == 'POST':
        E.encform = EncryptionForm(request.POST)
        km = KeyManager()
        if not km.mounted:
            E.mountform = MountStrongBoxForm(request.POST)
            if E.mountform.is_valid():
                pass
            else:
                E.template = 'bkp/management/new_encryption.html'
                return E.render()
        if E.encform.is_valid():
            enc = E.encform.save()
            location = reverse('list_encryptions')
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/new_encryption.html'
            return E.render()


@authentication_required
def main_management(request):
    E = ENV(request)

    if request.method == 'GET':
        E.template = 'bkp/management/main_management.html'
        return E.render()


@authentication_required
def list_computers(request):
    E = ENV(request)

    if request.method == 'GET':
        E.comp_list = E.computers
        E.template = 'bkp/management/list_computers.html'
        return E.render()


@authentication_required
def list_storages(request):
    E = ENV(request)

    if request.method == 'GET':
        E.sto_list = Storage.objects.all()
        E.template = 'bkp/management/list_storages.html'
        return E.render()


@authentication_required
def manage_strongbox(request):
    E = ENV(request)
    km = KeyManager()
    
    if not km.has_drive():
        location = reverse("new_strongbox")
        return HttpResponseRedirect(location)

    if request.method == 'GET':
        E.drive_mounted = km.mounted
        if not E.drive_mounted:
            E.mountstrongbox_form = MountStrongBoxForm()
        E.template = 'bkp/management/manage_strongbox.html'
        return E.render()


@authentication_required
def mount_strongbox(request):
    E = ENV(request)
    km = KeyManager()
    
    if not km.has_drive():
        location = reverse("new_strongbox")
        return HttpResponseRedirect(location)
    if km.mounted:
        location = reverse("manage_strongbox")
        return HttpResponseRedirect(location)

    if request.method == 'POST':
        E.mountstrongbox_form = MountStrongBoxForm(request.POST)
        if E.mountstrongbox_form.is_valid():
            location = reverse("manage_strongbox")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/manage_strongbox.html'
            return E.render()


@authentication_required
def new_strongbox(request):
    E = ENV(request)
    km = KeyManager()
    
    if km.has_drive():
        location = reverse("manage_strongbox")
        return HttpResponseRedirect(location)

    if request.method == 'GET':
        E.newstrongbox_form = NewStrongBoxForm(request.POST)
        E.template = 'bkp/management/new_strongbox.html'
        return E.render()


@authentication_required
def create_strongbox(request):
    E = ENV(request)
    km = KeyManager()
    
    if km.has_drive():
        location = reverse("manage_strongbox")
        return HttpResponseRedirect(location)

    if request.method == 'POST':
        E.newstrongbox_form = NewStrongBoxForm(request.POST)
        if E.newstrongbox_form.is_valid():
            location = reverse("manage_strongbox")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/new_strongbox.html'
            return E.render()


@authentication_required
def umount_strongbox(request):
    E = ENV(request)    
    km = KeyManager()
    
    if not km.mounted:
        location = reverse("manage_strongbox")
        return HttpResponseRedirect(location)

    if request.method == 'GET':
        E.umount_form = UmountStrongBoxForm()
        E.template = 'bkp/management/umount_strongbox.html'
        return E.render()
    elif request.method == 'POST':
        E.umount_form = UmountStrongBoxForm(request.POST)
        if E.umount_form.is_valid():
            if "sb_forceumount" in E.umount_form.cleaned_data:
                force = E.umount_form.cleaned_data["sb_forceumount"]
            else:
                force = False
            drive_umounted = km.umount_drive(force=force)
            if km.mounted:
                E.msg = _("Unable to lock strongbox.")
                location = reverse("umount_strongbox")
            else:
                E.msg = _("Strongbox successfully locked.")
                location = reverse("manage_strongbox")
            return HttpResponseRedirect(location)


@authentication_required
def changepwd_strongbox(request):
    E = ENV(request)
    km = KeyManager()

    if request.method == 'GET':
        E.changepwdsb_form = ChangePwdStrongBoxForm()
        E.template = 'bkp/management/changepwd_strongbox.html'
        return E.render()
    elif request.method == 'POST':
        E.changepwdsb_form = ChangePwdStrongBoxForm(request.POST)
        if E.changepwdsb_form.is_valid():
            location = reverse("manage_strongbox")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/changepwd_strongbox.html'
            return E.render()


@authentication_required
def new_headerbkp(request):
    E = ENV(request)
    
    if request.method == 'GET':
        E.headerbkp_form = HeaderBkpForm()
        E.template = 'bkp/management/new_headerbkp.html'
        return E.render()


@authentication_required
def create_headerbkp(request):
    E = ENV(request)
    
    if request.method == 'POST':
        E.headerbkp_form = HeaderBkpForm(request.POST, instance=HeaderBkp())
        if E.headerbkp_form.is_valid():
            E.headerbkp_form.save()
            location = reverse("list_headerbkp")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/new_headerbkp.html'
            return E.render()


@authentication_required
def list_headerbkp(request):
    E = ENV(request)
    
    if request.method == 'GET':
        E.hbkp_list = HeaderBkp.objects.all()
        E.template = 'bkp/management/list_headerbkp.html'
        return E.render()


@authentication_required
def delete_headerbkp(request, hbkp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.template = 'bkp/management/delete_headerbkp.html'
        return E.render()
    elif request.method == 'POST':
        headerbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        headerbkp.delete()
        location = reverse("list_headerbkp")
        return HttpResponseRedirect(location)


@authentication_required
def edit_headerbkp(request, hbkp_id):
    E = ENV(request)
    
    if request.method == 'GET':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.headerbkp_form = EditHeaderBkpForm(instance=E.hbkp)
        E.template = 'bkp/management/edit_headerbkp.html'
        return E.render()


@authentication_required
def update_headerbkp(request, hbkp_id):
    E = ENV(request)
    
    if request.method == 'POST':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.headerbkp_form = EditHeaderBkpForm(request.POST, instance=E.hbkp)
        if E.headerbkp_form.is_valid():
            E.headerbkp_form.save()
            location = reverse("list_headerbkp")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/edit_headerbkp.html'
            return E.render()


@authentication_required
def restore_headerbkp(request, hbkp_id):
    E = ENV(request)
    E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
    
    if request.method == 'GET':
        E.restorehbkp_form = RestoreHeaderBkpForm(instance=E.hbkp)
        E.template = 'bkp/management/restore_headerbkp.html'
        return E.render()
    elif request.method == 'POST':
        E.restorehbkp_form = RestoreHeaderBkpForm(request.POST, instance=E.hbkp)
        if E.restorehbkp_form.is_valid():
            location = reverse("list_headerbkp")
            return HttpResponseRedirect(location)
        else:
            E.template = 'bkp/management/restore_headerbkp.html'
            return E.render()