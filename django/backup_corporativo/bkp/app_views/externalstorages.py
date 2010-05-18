#!/usr/bin/env python
# -*- coding: UTF-8 -*-



from django.shortcuts import get_object_or_404
from backup_corporativo.bkp import utils, models, forms
from backup_corporativo.bkp.views import (allow_get, allow_post,
                                         render, make_list_generic_view_dict)


EXTERNALSTORAGE_CONFIRMATION_MSG = "Computador de armazenamento adicionado com sucesso"



@allow_get
def new_or_edit_external_storage(request, device_id=None):

    form = forms.ExternalStorageForm()

    if device_id:
        device = get_object_or_404(models.Device, pk=device_id)
        form.load_data_from_device(device)
        title = "Editar computador de armazenamento"
        button_label = "Editar"
        view_url = utils.reverse('update_external_storage',args=(device_id,))
    else:
        title = "Adicionar novo computador de armazenamento"
        button_label = "Adicionar"
        view_url = utils.reverse('create_external_storage')


    return render(request, "bkp/externalstorage/new_externalstorage.html", 
                {"form": form, "page_title": title, "button_label" : button_label,
                 "view_url" : view_url })



@allow_post
def create_or_update_external_storage(request, device_id=None):
    form = forms.ExternalStorageForm(request.POST)

    if form.is_valid():
        cleaned = form.cleaned_data

        if device_id:
            device = get_object_or_404(models.Device, pk=device_id)
            storage = device.storage
            msg = "Edição concluída com sucesso"
        else:
            device = models.Device()
            storage = models.Storage()
            msg = "Adição concluída com sucesso"


        storage.storage_name = cleaned['name']
        storage.storage_ip = cleaned['ip']
        storage.storage_port = cleaned['port']
        storage.storage_password = cleaned['password']
        storage.storage_description = cleaned['description']
        storage.save()

        device.name=cleaned['device_name']
        device.storage=storage
        device.save()

        request.user.message_set.create(message=msg)
        return utils.redirect('list_externalstorages')
    else:
        return render(request, "bkp/externalstorage/new_externalstorage.html", 
                     {"form": form})



@allow_get
def list_externalstorages(request):
    return render(request, "bkp/management/list_externalstorages.html", 
                                    {"object_list": models.Device.objects.all()})
