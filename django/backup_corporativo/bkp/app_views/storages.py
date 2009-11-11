#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from environment import ENV as E

from backup_corporativo.bkp.utils import reverse
from backup_corporativo.bkp.models import Storage, Procedure, GlobalConfig
from backup_corporativo.bkp.forms import StorageForm
from backup_corporativo.bkp.views import global_vars, authentication_required


@authentication_required
def new_storage(request):
    E.update(request)

    if request.method == 'GET':
        E.stoform = StorageForm()
        E.template = 'bkp/storage/new_storage.html',
        return E.render()


@authentication_required
def create_storage(request):
    E.update(request)

    if request.method == 'POST':
        E.stoform = StorageForm(request.POST)
        if E.stoform.is_valid():
            sto = E.stoform.save()
            location = reverse(view_storage, args=[sto.id])
            return HttpResponseRedirect(location)
        else:
            E.msg = _("Error at storage creation.")
            E.template = 'bkp/storage/new_storage.html'
            return E.render()


@authentication_required
def view_storage(request, sto_id):
    E.update(request)

    if request.method == 'GET':
        E.storage = get_object_or_404(Storage, pk=sto_id)
        E.procedures = Procedure.objects.filter(storage=E.storage)
        E.template = 'bkp/storage/view_storage.html',
        return E.render()


@authentication_required
def edit_storage(request, sto_id):
    E.update(request)
    
    if request.method == 'GET':
        E.storage = get_object_or_404(Storage, pk=sto_id)
        E.stoform = StorageForm(instance=E.storage)
        E.template = 'bkp/storage/edit_storage.html'
        return E.render()
        

@authentication_required
def update_storage(request, sto_id):
    E.update(request)
    if request.method == 'POST':
        E.storage = get_object_or_404(Storage, pk=sto_id)
        E.stoform = StorageForm(request.POST, instance=E.storage)
        if E.stoform.is_valid():
            sto = E.stoform.save()
            E.msg = _("Storage successfully updated.")
            location = reverse('view_storage', args=[sto.id])
            return HttpResponseRedirect(location)
        else:
            E.msg = _("Error at storage edition.")
            E.template = 'bkp/storage/edit_storage.html'
            E.render()


@authentication_required
def delete_storage(request, sto_id):
    E.update(request)
    
    if request.method == 'GET':
        E.storage = get_object_or_404(Storage, pk=sto_id)
        E.msg = _("Confirm storage removal.")
        E.template = 'bkp/storage/delete_storage.html'
        return E.render()
    elif request.method == 'POST':
        storage = get_object_or_404(Storage, pk=sto_id)
        storage.delete()
        E.msg = _("Storage has been successfully removed.")
        location = reverse('list_storages')
        return HttpResponseRedirect(location)


@authentication_required
def dump_storage_config(request, sto_id):
    """Generates and offers to download a storage config file."""
    storage = Storage.objects.get(id=sto_id)
    dump_list = storage.dump_storagedaemon_config()
    dump_file = ''.join(dump_list)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=bacula-sd.conf'
    response.write(dump_file)
    return response


@authentication_required
def view_storage_config(request, sto_id):
    E.update(request)
    
    if request.method == 'GET':
        E.sto = Storage.objects.get(pk=sto_id)
        E.storage_config = E.sto.dump_storagedaemon_config()
        E.template = 'bkp/storage/view_storage_config.html'
        return E.render()