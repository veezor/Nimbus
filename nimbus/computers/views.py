# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse

from nimbus.computers.models import Computer
from nimbus.shared.views import render_to_response




def add(request):
    extra_context = {'title': u"Adicionar computador"}
    return create_update.create_object( request, 
                                        model = Computer,
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/base/home")



def edit(request, object_id):
    extra_context = {'title': u"Editar computador"}
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        model = Computer,
                                        template_name = "base_computers.html",
                                        extra_context = extra_context,
                                        post_save_redirect = "/base/home")



def delete(request):
    pass

def list(request):
    computers = Computer.objects.all()
    return render_to_response(request, "computers_list.html", {'computers': computers})


