# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from nimbus.storages.models import Storage
from nimbus.storages.models import Device
from nimbus.storages.forms import StorageForm
from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form


# def add(request):
#     extra_context = {'title': u"Adicionar armazenamento"}
#     return create_update.create_object( request, 
#                                         model = Storage,
#                                         form_class = form(Storage),
#                                         template_name = "base_storages.html",
#                                         extra_context = extra_context,
#                                         post_save_redirect = "/storages/list")

def add(request):
    title = u"Adicionar armazenamento"
    storages = Storage.objects.filter(active=False)
    if request.method == "POST":
        print request.POST
        # computer_id
        messages.success(request, u"Armazenamento ativado com sucesso.")
        return redirect('nimbus.storages.views.list')

    return render_to_response(request, "storages_add.html", locals())



def edit(request, object_id):
    extra_context = {'title': u"Editar armazenamento"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Storage,
                                        form_class = form(Storage),
                                        template_name = "base_storages.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/storages/list")


def list(request):
    d = {
        "storages" : Storage.objects.filter(active=True),
        "title": u"Armazenamento"
    }
    return render_to_response(request, "storages_list.html", d)
    
    # extra_content = {"object_list": Device.objects.all()}
    # return render_to_response(request, "list_storages.html", extra_content)


def view(request, object_id):
    storage = Storage.objects.get(id=object_id)
    d = {
        "storage" : storage,
        "title": u"Armazenamento"
    }
    return render_to_response(request, "storages_view.html", d)


def view_computer(request, object_id):
    storage = Storage.objects.get(id=object_id)
    computers = Computer.objects.filter(procedure__profile__storage=storage)
    d = {
        "storage" : storage,
        "computers" : computers,
        "title": u'Computadores do armazenamento "%s"' % storage.name
    }
    return render_to_response(request, "computers_list.html", d)


def activate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = 1
    storage.save()
    
    # messages.success(u'Armazenamento ativado com sucesso.')
    return redirect('/storages/list')


def deactivate(request, object_id):
    storage = Storage.objects.get(id=object_id)
    storage.active = 0
    storage.save()

    # messages.success(u'Armazenamento ativado com sucesso.')
    return redirect('/storages/list')

