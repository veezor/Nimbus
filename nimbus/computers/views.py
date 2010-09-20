# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response
from nimbus.shared.forms import form




def add(request):
    extra_context = {'title': u"Adicionar computador"}
    return create_update.create_object( request, 
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")



def edit(request, object_id):
    extra_context = {'title': u"Editar computador"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        form_class = form(Computer),
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/computers/")



def delete(request):
    pass

def list(request):
    computers = Computer.objects.all()
    extra_content = {
        'computers': computers,
        'title': u"Computadores"
    }
    return render_to_response(request, "computers_list.html", extra_content)


def view(request, object_id):
    computers = Computer.objects.get(id=object_id)
    extra_content = {
        'computer': computers,
        'title': u"Visualizar computador"
    }
    return render_to_response(request, "computers_view.html", extra_content)
