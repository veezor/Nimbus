# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.storages.models import Storage
from nimbus.storages.models import Device
from nimbus.storages.forms import StorageForm
from nimbus.shared.views import render_to_response


def add(request):
    extra_context = {'title': u"Adicionar armazenamento"}
    return create_update.create_object( request, 
                                        model = Storage,
                                        # model = StorageForm,
                                        template_name = "base_storages.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/storages/list")



def edit(request, object_id):
    extra_context = {'title': u"Editar armazenamento"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Storage,
                                        template_name = "base_storages.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/storages/list")


def list(request):
    d = {
        "storages" : Storage.objects.all(),
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