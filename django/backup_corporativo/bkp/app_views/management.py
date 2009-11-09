#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy

from Environment import ENV as E
from keymanager import KeyManager

from backup_corporativo.bkp import utils
from backup_corporativo.bkp.models import Storage, HeaderBkp
from backup_corporativo.bkp.forms import NewStrongBoxForm, MountStrongBoxForm, HeaderBkpForm, UmountStrongBoxForm, RestoreHeaderBkpForm, ChangePwdStrongBoxForm
from backup_corporativo.bkp.views import global_vars, authentication_required



@authentication_required
def main_management(request):
    E.update(request)

    if request.method == 'GET':
        E.template = 'bkp/management/main_management.html'
        return E.render()


@authentication_required
def list_computers(request):
    E.update(request)

    if request.method == 'GET':
        E.comp_list = E.computers
        E.template = 'bkp/management/list_computers.html'
        return E.render()


@authentication_required
def list_storages(request):
    E.update(request)

    if request.method == 'GET':
        E.sto_list = Storage.objects.all()
        E.template = 'bkp/management/list_storages.html'
        return E.render()


@authentication_required
def manage_strongbox(request):
    E.update(request)
    km = KeyManager()
    
    if not km.has_drive():
        return HttpResponseRedirect(utils.new_strongbox_path(request))

    if request.method == 'GET':
        E.drive_mounted = km.mounted
        if not E.drive_mounted:
            E.mountstrongbox_form = MountStrongBoxForm()
        E.template = 'bkp/management/manage_strongbox.html'
        return E.render()


@authentication_required
def mount_strongbox(request):
    E.update(request)
    km = KeyManager()
    
    if not km.has_drive():
        return HttpResponseRedirect(utils.new_strongbox_path(request))
    if km.mounted:
        return HttpResponseRedirect(utils.manage_strongbox_path(request))

    if request.method == 'POST':
        E.mountstrongbox_form = MountStrongBoxForm(request.POST)
        if E.mountstrongbox_form.is_valid():
            return HttpResponseRedirect(utils.manage_strongbox_path(request))
        else:
            E.template = 'bkp/management/manage_strongbox.html'
            return E.render()


@authentication_required
def new_strongbox(request):
    E.update(request)
    km = KeyManager()
    
    if km.has_drive():
        return HttpResponseRedirect(utils.manage_strongbox_path(request))

    if request.method == 'GET':
        E.newstrongbox_form = NewStrongBoxForm(request.POST)
        E.template = 'bkp/management/new_strongbox.html'
        return E.render()


@authentication_required
def create_strongbox(request):
    E.update(request)
    km = KeyManager()
    
    if km.has_drive():
        return HttpResponseRedirect(utils.manage_strongbox(request))

    if request.method == 'POST':
        E.newstrongbox_form = NewStrongBoxForm(request.POST)
        if E.newstrongbox_form.is_valid():
            return HttpResponseRedirect(utils.manage_strongbox_path(request))
        else:
            E.template = 'bkp/management/new_strongbox.html'
            return E.render()


@authentication_required
def umount_strongbox(request):
    E.update(request)    
    km = KeyManager()
    
    if not km.mounted:
        return HttpResponseRedirect(utils.manage_strongbox_path(request))

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
                E.msg = _("Unable to umount strongbox.")
                return HttpResponseRedirect(utils.umount_strongbox_path(request))
            else:
                return HttpResponseRedirect(utils.manage_strongbox_path(request))


@authentication_required
def changepwd_strongbox(request):
    E.update(request)
    km = KeyManager()

    if request.method == 'GET':
        E.changepwdsb_form = ChangePwdStrongBoxForm()
        E.template = 'bkp/management/changepwd_strongbox.html'
        return E.render()
    elif request.method == 'POST':
        E.changepwdsb_form = ChangePwdStrongBoxForm(request.POST)
        if E.changepwdsb_form.is_valid():
            return HttpResponseRedirect(utils.manage_strongbox_path(request))
        else:
            E.template = 'bkp/management/changepwd_strongbox.html'
            return E.render()


@authentication_required
def new_headerbkp(request):
    E.update(request)
    
    if request.method == 'GET':
        E.headerbkp_form = HeaderBkpForm()
        E.template = 'bkp/management/new_headerbkp.html'
        return E.render()


@authentication_required
def create_headerbackup(request):
    E.update(request)
    
    if request.method == 'POST':
        E.headerbkp_form = HeaderBkpForm(request.POST, instance=HeaderBkp())
        if E.headerbkp_form.is_valid():
            E.headerbkp_form.save()
            return HttpResponseRedirect(utils.list_headerbkp_path(request))
        else:
            E.template = 'bkp/management/new_headerbkp.html'
            return E.render()


@authentication_required
def list_headerbkp(request):
    E.update(request)
    
    if request.method == 'GET':
        E.hbkp_list = HeaderBkp.objects.all()
        E.template = 'bkp/management/list_headerbkp.html'
        return E.render()


@authentication_required
def delete_headerbkp(request, hbkp_id):
    E.update(request)
    
    if request.method == 'GET':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.template = 'bkp/management/delete_headerbkp.html'
        return E.render()
    elif request.method == 'POST':
        headerbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        headerbkp.delete()
        return HttpResponseRedirect(utils.list_headerbkp_path(request))


@authentication_required
def edit_headerbkp(request, hbkp_id):
    E.update(request)
    
    if request.method == 'GET':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.headerbkp_form = HeaderBkpForm(instance=E.hbkp)
        E.template = 'bkp/management/edit_headerbkp.html'
        return E.render()


@authentication_required
def update_headerbkp(request, hbkp_id):
    E.update(request)
    
    if request.method == 'POST':
        E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
        E.headerbkp_form = HeaderBkpForm(request.POST, instance=E.hbkp)
        if E.headerbkp_form.is_valid():
            E.headerbkp_form.save()
            return HttpResponseRedirect(utils.list_headerbkp_path(request))
        else:
            E.template = 'bkp/management/edit_headerbkp.html'
            return E.render()


@authentication_required
def restore_headerbkp(request, hbkp_id):
    E.update(request)
    E.hbkp = get_object_or_404(HeaderBkp, pk=hbkp_id)
    
    if request.method == 'GET':
        E.restorehbkp_form = RestoreHeaderBkpForm(instance=E.hbkp)
        E.template = 'bkp/management/restore_headerbkp.html'
        return E.render()
    elif request.method == 'POST':
        E.restorehbkp_form = RestoreHeaderBkpForm(request.POST, instance=hbkp)
        if E.restorehbkp_form.is_valid():
            return HttpResponseRedirect(utils.list_headerbkp_path(request))
        else:
            E.template = 'bkp/management/restore_headerbkp.html'
            return E.render()