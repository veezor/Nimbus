# Create your views here.

from django.views.generic import create_update
from django.core.urlresolvers import reverse


from nimbus.computers.forms import ComputerForm


def add(request):
    return create_update.create_object( request, 
                                        form_class = ComputerForm, 
                                        template_name = "genericform.html")



def edit(request, object_id):
    return create_update.update_object( request, 
                                        object_id = object_id,
                                        form_class = ComputerForm, 
                                        template_name = "genericform.html")



def delete(request):
    pass

def list(request):
    pass


